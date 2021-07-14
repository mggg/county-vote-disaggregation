import pandas as pd
import geopandas as gpd
import maup
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.colors as colors
from functools import partial
from disaggregation_methods import *
import csv
import os
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error,median_absolute_error,mean_absolute_percentage_error




figs_dir = "./figs/"
os.makedirs(os.path.dirname(figs_dir), exist_ok=True)
data_dir = "./output_data/"
os.makedirs(os.path.dirname(data_dir), exist_ok=True)

state = 'NC' #'NC' or 'OK'

if state == 'OK':
    returns_path = './data/OK_election_returns.csv'
    shapefile_path = './data/OK_shapefile'
    history_path = './data/OK_voter_history.csv'
    returns_name_dict = {'method_col':'Method','county_col':'County','contest_col':'Contest','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    shapefile_name_dict = {'county_col':'County', 'id_col':'Precinct', 'totpop_col':'TOTPOP', 'vap_col':'VAP', 'area_col':'AREA'}
    history_name_dict = {'method_col':'Method','county_col':'County','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    elections_of_interest = {2020:'11/03/2020',2016:'11/08/2016'}
    contests_of_interest = {2020:['PRES'],2016:['PRES']}
    method_list = ['Absentee','Early']
    party_list = ['DEM','REP']
    day_of_label = 'In Person'
elif state == 'NC':
    returns_path = './data/NC_election_returns.csv'
    shapefile_path = './data/NC_shapefile'
    history_path = './data/NC_voter_history.csv'
    returns_name_dict = {'method_col':'Method','county_col':'County','contest_col':'Contest','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    shapefile_name_dict = {'county_col':'County', 'id_col':'Precinct', 'totpop_col':'TOTPOP', 'vap_col':'VAP', 'area_col':'AREA'}
    history_name_dict = {'method_col':'Method','county_col':'County','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    elections_of_interest = {2020:'11/03/2020',2016:'11/08/2016'}
    contests_of_interest = {2020:['PRES'],2016:['PRES']}
    method_list = ['Absentee','Early']
    party_list = ['DEM','REP']
    day_of_label = 'In Person'
else:
    print('Unknown state')
    assert False


returns = pd.read_csv(returns_path)
history = pd.read_csv(history_path)
shapefile = gpd.read_file(shapefile_path)

strategy_scores = []

for year in elections_of_interest.keys():
    for contest in contests_of_interest[year]:
        for method in method_list:
            for party in party_list:
                elec_date = elections_of_interest[year]
                returns_of_interest = returns[(returns[returns_name_dict['date_col']]==elec_date)&(returns[returns_name_dict['contest_col']]==contest)&(returns[returns_name_dict['party_col']]==party)&(returns[returns_name_dict['method_col']]==method)]
                returns_of_interest['county_sums'] = returns_of_interest.groupby(returns_name_dict['county_col'])[returns_name_dict['vote_col']].transform('sum')
                county_sum_dict = pd.Series(returns_of_interest['county_sums'].values,index=returns_of_interest[returns_name_dict['id_col']]).to_dict()
                ground_truth_count_dict = pd.Series(returns_of_interest[returns_name_dict['vote_col']].values,index=returns_of_interest[returns_name_dict['id_col']]).to_dict()
                ground_truth_pct_dict = {key:ground_truth_count_dict[key]/county_sum_dict[key] for key in county_sum_dict if county_sum_dict[key]>0}


                strategy_dict = {
                    'by_area':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['area_col'], county_col = shapefile_name_dict['county_col']),
                    'by_vap':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['vap_col'], county_col = shapefile_name_dict['county_col']),
                    'by_totpop':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['totpop_col'], county_col = shapefile_name_dict['county_col']),
                    'by_day_of':partial(dist_as_day_of, election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], method_col = returns_name_dict['method_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, party_col = returns_name_dict['party_col'], party_lbl = party, date_col = returns_name_dict['date_col'], date_lbl= elec_date,votes_col = returns_name_dict['vote_col']),
                    'by_voterfile_tot_votes':partial(dist_as_voter_file_total_votes,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col = history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col']),
                    'by_voterfile_method':partial(dist_as_voter_file_method,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col= history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], method_col= history_name_dict['method_col'], method_lbl= method),
                    'by_voterfile_party':partial(dist_as_voter_file_party,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col= history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], party_col= history_name_dict['party_col'], party_lbl = party),
                    'by_voterfile_method_party':partial(dist_as_voter_file_method_and_party,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col = history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], method_col= history_name_dict['method_col'], method_lbl = method, party_col = history_name_dict['party_col'], party_lbl= party),
                    'by_voterfile_minus_day_of':partial(dist_as_voter_file_minus_day_of,election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], method_col= returns_name_dict['method_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, party_col = returns_name_dict['party_col'], party_lbl= party, date_col= returns_name_dict['date_col'], date_lbl = elec_date,votes_col= returns_name_dict['vote_col'], voterfile_df = history, voterfile_id = history_name_dict['id_col'], voterfile_county_col = history_name_dict['county_col'], voterfile_date_col = history_name_dict['date_col'], voterfile_date_lbl = elec_date, voterfile_votes_col = history_name_dict['vote_col'], scale = False),
                    'by_scaled_voterfile_minus_day_of':partial(dist_as_voter_file_minus_day_of,election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], method_col= returns_name_dict['method_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, party_col = returns_name_dict['party_col'], party_lbl= party, date_col= returns_name_dict['date_col'], date_lbl= elec_date,votes_col= returns_name_dict['vote_col'], voterfile_df= history, voterfile_id = history_name_dict['id_col'], voterfile_county_col = history_name_dict['county_col'], voterfile_date_col = history_name_dict['date_col'], voterfile_date_lbl = elec_date, voterfile_votes_col = history_name_dict['vote_col'], scale = True)
                }
                for strategy in strategy_dict.keys():
                    run_name = '_'.join([str(x) for x in [state,year,contest,party,method,strategy]])
                    strategy_proportion_dict = strategy_dict[strategy]()
                    count_estimates = {key:strategy_proportion_dict[key]*county_sum_dict[key] for key in county_sum_dict.keys() if key in strategy_proportion_dict.keys()}
                    counts_target = [ground_truth_count_dict[key] for key in count_estimates.keys()]
                    counts_pred = [count_estimates[key] for key in count_estimates.keys()]
                    pct_target = [ground_truth_pct_dict[key] for key in strategy_proportion_dict.keys() if key in ground_truth_pct_dict.keys()]
                    pct_pred = [strategy_proportion_dict[key] for key in strategy_proportion_dict.keys() if key in ground_truth_pct_dict.keys()]

                    scatter_fig(counts_target,counts_pred, 0.95,strategy,method,party,figs_dir+run_name+'_counts_scatter.png')
                    error_fig(counts_target,counts_pred, 10,strategy,method,party,figs_dir+run_name+'_error.png')
                    scatter_fig(pct_target,pct_pred, 1,strategy,method,party,figs_dir+run_name+'_pct_scatter.png')

                    pct_r2 = r2_score(pct_target, pct_pred)
                    pct_rmse = mean_squared_error(pct_target, pct_pred, squared=False)
                    pct_mean_abs_error = mean_absolute_error(pct_target, pct_pred)
                    pct_median_abs_error = median_absolute_error(pct_target, pct_pred)
                    pct_mean_abs_pct_error = mean_absolute_percentage_error(pct_target, pct_pred)
                    counts_r2 = r2_score(counts_target, counts_pred)
                    counts_rmse = mean_squared_error(counts_target, counts_pred, squared=False)
                    counts_mean_abs_error = mean_absolute_error(counts_target, counts_pred)
                    counts_median_abs_error = median_absolute_error(counts_target, counts_pred)
                    counts_mean_abs_pct_error = mean_absolute_percentage_error(counts_target, counts_pred)
                    strategy_scores.append([state,year,contest,party,method,strategy,pct_r2,pct_rmse,pct_mean_abs_error,pct_median_abs_error,pct_mean_abs_pct_error,counts_r2,counts_rmse,counts_mean_abs_error,counts_median_abs_error,counts_mean_abs_pct_error])


with open(data_dir+state+'_scores.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['state','year','contest','party','vote_method','strategy','pct_r2','pct_rmse','pct_mean_abs_error','pct_median_abs_error','pct_mean_abs_pct_error','counts_r2','counts_rmse','counts_mean_abs_error','counts_median_abs_error','counts_mean_abs_pct_error'])
    writer.writerows(strategy_scores)