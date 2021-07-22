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

#set up directories
figs_dir = "./figs/"
os.makedirs(os.path.dirname(figs_dir), exist_ok=True)
data_dir = "./output_data/"
os.makedirs(os.path.dirname(data_dir), exist_ok=True)

state = 'OK' #'NC' or 'OK'
record_error_scores = True

if state == 'OK':
    returns_path = './data/OK_election_returns.csv'
    shapefile_paths = {y:'./data/OK_shapefile' for y in [2016,2020]}
    history_path = './data/OK_voter_history.csv'
    returns_name_dict = {'mode_col':'Method','county_col':'County','contest_col':'Contest','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    shapefile_name_dict = {'county_col':'County', 'id_col':'Precinct', 'totpop_col':'TOTPOP', 'vap_col':'TOTVAP', 'cvap_col':'CVAP', 'area_col':'AREA'}
    history_name_dict = {'mode_col':'Method','county_col':'County','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    elections_of_interest = {2020:'11/03/2020',2016:'11/08/2016'}
    contests_of_interest = {2020:['PRES'],2016:['PRES']}
    mode_list = ['Absentee','Early']
    party_list = ['DEM','REP']
    day_of_label = 'In Person'
    county_exclude = [55,72]
elif state == 'NC':
    returns_path = './data/NC_election_returns.csv'
    shapefile_paths = {2016:'./data/NC_prec_2016',2020:'./data/NC_prec_2020'}
    history_path = './data/NC_voter_history.csv'
    returns_name_dict = {'mode_col':'Method','county_col':'County','contest_col':'Contest','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    shapefile_name_dict = {'county_col':'County', 'id_col':'Precinct', 'totpop_col':'TOTPOP', 'vap_col':'TOTVAP','cvap_col':'CVAP', 'area_col':'AREA'}
    history_name_dict = {'mode_col':'Method','county_col':'County','party_col':'Party','date_col':'Date','id_col':'Precinct','vote_col':'Votes'}
    elections_of_interest = {2020:'11/03/2020',2016:'11/08/2016'}
    contests_of_interest = {2020:['PRES'],2016:['PRES']}
    mode_list = ['Absentee','Early']
    party_list = ['DEM','REP']
    day_of_label = 'In Person'
    NC_2020_dist_col = 'NC_House_dist2020'
    NC_2020_dist_cov_col = 'pct_dist_coverage2020'
    county_exclude = []
else:
    print('Unknown state')
    assert False

strategies = ['uniform', 'by_area', 'by_vap', 'by_cvap', 'by_totpop', 'by_day_of', 'by_voterfile_tot_votes', 'by_voterfile_mode', 'by_voterfile_party', 'by_voterfile_mode_party', 'by_voterfile_minus_day_of', 'by_scaled_voterfile_minus_day_of']


returns = pd.read_csv(returns_path)
history = pd.read_csv(history_path)

strategy_scores = []

for year in elections_of_interest.keys():
    for contest in contests_of_interest[year]:
        shapefile = gpd.read_file(shapefile_paths[year])
        elec_date = elections_of_interest[year]
        total_votes = returns[(returns[returns_name_dict['date_col']]==elec_date)&(returns[returns_name_dict['contest_col']]==contest)&(returns[returns_name_dict['party_col']].isin(party_list))&(~returns[returns_name_dict['county_col']].isin(county_exclude))][[returns_name_dict['county_col'],returns_name_dict['id_col'],returns_name_dict['party_col'],returns_name_dict['vote_col']]].groupby([returns_name_dict['county_col'],returns_name_dict['id_col'],returns_name_dict['party_col']]).sum().reset_index()
        total_votes = total_votes.set_index([returns_name_dict['id_col'], returns_name_dict['county_col'],returns_name_dict['party_col']])[returns_name_dict['vote_col']].unstack().reset_index()
        prec_to_county_lookup = pd.Series(total_votes[[returns_name_dict['county_col'],returns_name_dict['id_col']]].drop_duplicates()[returns_name_dict['county_col']].values,index=total_votes[[returns_name_dict['county_col'],returns_name_dict['id_col']]].drop_duplicates()[returns_name_dict['id_col']]).to_dict()
        for mode in mode_list+[day_of_label]:
            mode_votes = returns[(returns[returns_name_dict['date_col']]==elec_date)&(returns[returns_name_dict['contest_col']]==contest)&(returns[returns_name_dict['party_col']].isin(party_list))&(returns[returns_name_dict['mode_col']]==mode)][[returns_name_dict['county_col'],returns_name_dict['id_col'],returns_name_dict['party_col'],returns_name_dict['vote_col']]].groupby([returns_name_dict['county_col'],returns_name_dict['id_col'],returns_name_dict['party_col']]).sum().reset_index().rename(columns = {returns_name_dict['vote_col']:mode})
            mode_votes = mode_votes.set_index([returns_name_dict['id_col'], returns_name_dict['county_col'],returns_name_dict['party_col']])[mode].unstack().reset_index().rename(columns = {party:party+'_'+mode for party in party_list})
            total_votes = total_votes.merge(mode_votes[[returns_name_dict['id_col']]+[party+'_'+mode for party in party_list]], how = 'left', left_on = [returns_name_dict['id_col']], right_on = [returns_name_dict['id_col']]).fillna(0)
        #get county level aggregate values for party totals and party-mode combinations
        for party in party_list:
            total_votes[party+'_county'] = total_votes.groupby(returns_name_dict['county_col'])[party].transform('sum')
            for mode in mode_list:
                total_votes[party+'_'+mode+'_county'] = total_votes.groupby(returns_name_dict['county_col'])[party+'_'+mode].transform('sum')
        #Add day-of votes to the running sums for party total votes
        for strategy in strategies:
            for party in party_list:
                total_votes[party+'_'+strategy] = total_votes[party+'_'+day_of_label]
        
        #form estimates for each party-mode combination
        for mode in mode_list:
            for party in party_list:
                returns_of_interest = returns[(returns[returns_name_dict['date_col']]==elec_date)&(returns[returns_name_dict['contest_col']]==contest)&(returns[returns_name_dict['party_col']]==party)&(returns[returns_name_dict['mode_col']]==mode)&(~returns[returns_name_dict['county_col']].isin(county_exclude))]
                returns_of_interest['county_sums'] = returns_of_interest.groupby(returns_name_dict['county_col'])[returns_name_dict['vote_col']].transform('sum')                
                county_sum_dict = pd.Series(returns_of_interest[[returns_name_dict['county_col'],'county_sums']].drop_duplicates()['county_sums'].values,index=returns_of_interest[[returns_name_dict['county_col'],'county_sums']].drop_duplicates()[returns_name_dict['county_col']]).to_dict()
                ground_truth_count_dict = pd.Series(returns_of_interest[returns_name_dict['vote_col']].values,index=returns_of_interest[returns_name_dict['id_col']]).to_dict()
                ground_truth_pct_dict = {key:ground_truth_count_dict[key]/county_sum_dict[prec_to_county_lookup[key]] for key in ground_truth_count_dict if county_sum_dict[prec_to_county_lookup[key]]>0}
                strategy_dict = {
                    'uniform':partial(dist_uniform,election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], county_col = returns_name_dict['county_col'], date_col = returns_name_dict['date_col'], date_lbl = elec_date,contest_col = returns_name_dict['contest_col'] ,contest_lbl = contest),
                    'by_area':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['area_col'], county_col = shapefile_name_dict['county_col']),
                    'by_vap':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['vap_col'], county_col = shapefile_name_dict['county_col']),
                    'by_cvap':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['cvap_col'], county_col = shapefile_name_dict['county_col']),
                    'by_totpop':partial(dist_as_shapefile_col, shapefile_gdf = shapefile, shapefile_id = shapefile_name_dict['id_col'], shapefile_by_col = shapefile_name_dict['totpop_col'], county_col = shapefile_name_dict['county_col']),
                    'by_day_of':partial(dist_as_day_of, election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], mode_col = returns_name_dict['mode_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, party_col = returns_name_dict['party_col'], party_lbl = party, date_col = returns_name_dict['date_col'], date_lbl= elec_date,votes_col = returns_name_dict['vote_col']),
                    'by_voterfile_tot_votes':partial(dist_as_voter_file_total_votes,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col = history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col']),
                    'by_voterfile_mode':partial(dist_as_voter_file_mode,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col= history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], mode_col= history_name_dict['mode_col'], mode_lbl= mode),
                    'by_voterfile_party':partial(dist_as_voter_file_party,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col= history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], party_col= history_name_dict['party_col'], party_lbl = party),
                    'by_voterfile_mode_party':partial(dist_as_voter_file_mode_and_party,voterfile_df = history, voterfile_id = history_name_dict['id_col'], county_col = history_name_dict['county_col'], date_col = history_name_dict['date_col'], date_lbl = elec_date, votes_col = history_name_dict['vote_col'], mode_col= history_name_dict['mode_col'], mode_lbl = mode, party_col = history_name_dict['party_col'], party_lbl= party),
                    'by_voterfile_minus_day_of':partial(dist_as_voter_file_minus_day_of,election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], mode_col= returns_name_dict['mode_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, date_col= returns_name_dict['date_col'], date_lbl = elec_date,votes_col= returns_name_dict['vote_col'], voterfile_df = history, voterfile_id = history_name_dict['id_col'], voterfile_county_col = history_name_dict['county_col'], voterfile_date_col = history_name_dict['date_col'], voterfile_date_lbl = elec_date, voterfile_votes_col = history_name_dict['vote_col'], scale = False),
                    'by_scaled_voterfile_minus_day_of':partial(dist_as_voter_file_minus_day_of,election_returns_df = returns, election_returns_id = returns_name_dict['id_col'], mode_col= returns_name_dict['mode_col'], day_of_label = day_of_label, county_col = returns_name_dict['county_col'], contest_col = returns_name_dict['contest_col'], contest_lbl = contest, date_col= returns_name_dict['date_col'], date_lbl= elec_date,votes_col= returns_name_dict['vote_col'], voterfile_df= history, voterfile_id = history_name_dict['id_col'], voterfile_county_col = history_name_dict['county_col'], voterfile_date_col = history_name_dict['date_col'], voterfile_date_lbl = elec_date, voterfile_votes_col = history_name_dict['vote_col'], scale = True)
                }
                for strategy in strategy_dict.keys():   
                    strategy_proportion_dict = strategy_dict[strategy]()
                    count_estimates = {key:strategy_proportion_dict[key]*county_sum_dict[prec_to_county_lookup[key]] for key in strategy_proportion_dict.keys() if key in prec_to_county_lookup.keys()}
                    total_votes[party+'_'+strategy] = total_votes[party+'_'+strategy] + (total_votes[returns_name_dict['id_col']].map(count_estimates).fillna(0))
                    total_votes[party+'_'+mode+'_'+strategy] = total_votes[returns_name_dict['id_col']].map(count_estimates).fillna(0)

        

        for party in party_list:
            pred_dict = {}
            for strategy in strategies:
                # assert(total_votes[party+'_'+strategy].sum()==total_votes[party].sum())
                run_name = '_'.join([str(x) for x in [state,year,contest,party,strategy]])
                # pared_votes = total_votes[~total_votes[party+'_'+strategy].isna()]
                pared_votes = total_votes
                counts_target = list(pared_votes[party])
                counts_pred = list(pared_votes[party+'_'+strategy])
                pared_votes_pct = pared_votes[pared_votes[party+'_county']!=0]
                pct_target = list(pared_votes_pct[party]/pared_votes_pct[party+'_county'])
                pct_pred = list(pared_votes_pct[party+'_'+strategy]/pared_votes_pct[party+'_county'])
                pared_votes_partisan = pared_votes[((pared_votes[[p+'_'+strategy for p in party_list]].sum(axis=1))!=0)&(~(pared_votes[[p+'_'+strategy for p in party_list]].sum(axis=1)).isna())&((pared_votes[[p for p in party_list]].sum(axis=1))!=0)&(~(pared_votes[[p for p in party_list]].sum(axis=1)).isna())]
                partisan_target = list(pared_votes_partisan[party]/(pared_votes_partisan[[p for p in party_list]].sum(axis=1)))
                partisan_pred = list(pared_votes_partisan[party+'_'+strategy]/(pared_votes_partisan[[p+'_'+strategy for p in party_list]].sum(axis=1)))
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
                partisan_r2 = r2_score(partisan_target, partisan_pred)
                partisan_rmse = mean_squared_error(partisan_target, partisan_pred, squared=False)
                partisan_mean_abs_error = mean_absolute_error(partisan_target, partisan_pred)
                partisan_median_abs_error = median_absolute_error(partisan_target, partisan_pred)
                partisan_mean_abs_pct_error = mean_absolute_percentage_error(partisan_target, partisan_pred)
                strategy_scores.append([state,year,contest,party,'party',strategy,pct_r2,pct_rmse,pct_mean_abs_error,pct_median_abs_error,pct_mean_abs_pct_error,counts_r2,counts_rmse,counts_mean_abs_error,counts_median_abs_error,counts_mean_abs_pct_error,partisan_r2,partisan_rmse,partisan_mean_abs_error,partisan_median_abs_error,partisan_mean_abs_pct_error])

                for mode in mode_list:
                    mode_run_name = '_'.join([str(x) for x in [state,year,contest,party,mode,strategy]])
                    pared_votes = total_votes.copy().fillna(0)
                    counts_target = list(pared_votes[party+'_'+mode])
                    counts_pred = list(pared_votes[party+'_'+mode+'_'+strategy])
                    pared_votes_pct = pared_votes[pared_votes[party+'_'+mode+'_county']!=0]
                    pct_target = list(pared_votes_pct[party+'_'+mode]/pared_votes_pct[party+'_'+mode+'_county'])
                    pct_pred = list(pared_votes_pct[party+'_'+mode+'_'+strategy]/pared_votes_pct[party+'_'+mode+'_county'])
                    pared_votes_partisan = pared_votes[((pared_votes[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1))!=0)&(~(pared_votes[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1)).isna())&((pared_votes[[p+'_'+mode for p in party_list]].sum(axis=1))!=0)&(~(pared_votes[[p+'_'+mode for p in party_list]].sum(axis=1)).isna())]
                    partisan_target = list(pared_votes_partisan[party+'_'+mode]/(pared_votes_partisan[[p+'_'+mode for p in party_list]].sum(axis=1)))
                    partisan_pred = list(pared_votes_partisan[party+'_'+mode+'_'+strategy]/(pared_votes_partisan[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1)))
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
                    partisan_r2 = r2_score(partisan_target, partisan_pred)
                    partisan_rmse = mean_squared_error(partisan_target, partisan_pred, squared=False)
                    partisan_mean_abs_error = mean_absolute_error(partisan_target, partisan_pred)
                    partisan_median_abs_error = median_absolute_error(partisan_target, partisan_pred)
                    partisan_mean_abs_pct_error = mean_absolute_percentage_error(partisan_target, partisan_pred)
                    strategy_scores.append([state,year,contest,party,mode,strategy,pct_r2,pct_rmse,pct_mean_abs_error,pct_median_abs_error,pct_mean_abs_pct_error,counts_r2,counts_rmse,counts_mean_abs_error,counts_median_abs_error,counts_mean_abs_pct_error,partisan_r2,partisan_rmse,partisan_mean_abs_error,partisan_median_abs_error,partisan_mean_abs_pct_error])

        total_votes.to_csv(data_dir+'_'.join([state,str(year),contest])+'_est_votes.csv', index=False)
        if state == 'NC' and year == 2020:
            prec = returns[(returns[returns_name_dict['date_col']]==elec_date)][[returns_name_dict['id_col'],NC_2020_dist_col,NC_2020_dist_cov_col]].drop_duplicates()
            assert(len(prec)==prec[returns_name_dict['id_col']].nunique())
            total_votes = total_votes.merge(prec, how = 'left', left_on = returns_name_dict['id_col'], right_on = returns_name_dict['id_col'])
            dist_votes = total_votes.groupby([NC_2020_dist_col,NC_2020_dist_cov_col]).sum().reset_index().drop([returns_name_dict['county_col']]+[party+'_county' for party in party_list], axis=1)
            dist_votes.to_csv(data_dir+'_'.join([state,str(year),contest])+'_est_dist_votes.csv', index=False)


if record_error_scores:
    with open(data_dir+state+'_scores.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['state','year','contest','party','mode','strategy','pct_r2','pct_rmse','pct_mean_abs_error','pct_median_abs_error','pct_mean_abs_pct_error','counts_r2','counts_rmse','counts_mean_abs_error','counts_median_abs_error','counts_mean_abs_pct_error','partisan_r2','partisan_rmse','partisan_mean_abs_error','partisan_median_abs_error','partisan_mean_abs_pct_error'])
        writer.writerows(strategy_scores)


