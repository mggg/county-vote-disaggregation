import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.gridspec as gridspec
import seaborn as sns
import scipy.stats as stats


def dist_uniform(election_returns_df, election_returns_id, county_col,date_col, date_lbl,contest_col,contest_lbl):
    election_returns_pared = election_returns_df[(election_returns_df[contest_col]==contest_lbl)&(election_returns_df[date_col]==date_lbl)].groupby(election_returns_id).first().reset_index()
    assert(len(election_returns_pared)==election_returns_pared[election_returns_id].nunique())
    election_returns_pared['num_prec'] = election_returns_pared.groupby(county_col)[election_returns_id].transform('nunique')
    election_returns_pared['inv_num_prec'] = 1/election_returns_pared['num_prec']
    election_returns_pared = election_returns_pared[~election_returns_pared['inv_num_prec'].isna()]
    return pd.Series(election_returns_pared['inv_num_prec'].values,index=election_returns_pared[election_returns_id]).to_dict()

def dist_as_shapefile_col(shapefile_gdf, shapefile_id, shapefile_by_col, county_col):
    shapefile_pared = shapefile_gdf[[county_col,shapefile_id,shapefile_by_col]]
    shapefile_pared['county_dist_col_sum'] = shapefile_pared.groupby(county_col)[shapefile_by_col].transform('sum')
    shapefile_pared['county_dist_col_pct'] = shapefile_pared[shapefile_by_col]/shapefile_pared['county_dist_col_sum']
    shapefile_pared = shapefile_pared[~shapefile_pared['county_dist_col_pct'].isna()]
    return pd.Series(shapefile_pared['county_dist_col_pct'].values,index=shapefile_pared[shapefile_id]).to_dict()

def dist_as_day_of(election_returns_df, election_returns_id, mode_col, day_of_label, county_col, contest_col, contest_lbl, party_col, party_lbl, date_col, date_lbl,votes_col):
    election_returns_pared = election_returns_df[(election_returns_df[contest_col]==contest_lbl)&(election_returns_df[date_col]==date_lbl)&(election_returns_df[party_col]==party_lbl)&(election_returns_df[mode_col]==day_of_label)]
    assert(len(election_returns_pared)==election_returns_pared[election_returns_id].nunique())
    election_returns_pared['county_day_of_sum'] = election_returns_pared.groupby(county_col)[votes_col].transform('sum')
    election_returns_pared['county_day_of_pct'] = election_returns_pared[votes_col]/election_returns_pared['county_day_of_sum']
    election_returns_pared = election_returns_pared[~election_returns_pared['county_day_of_pct'].isna()]
    return pd.Series(election_returns_pared['county_day_of_pct'].values,index=election_returns_pared[election_returns_id]).to_dict()

def dist_as_voter_file_total_votes(voterfile_df, voterfile_id, county_col, date_col, date_lbl, votes_col):
    voterfile_pared = voterfile_df[voterfile_df[date_col]==date_lbl][[county_col,voterfile_id,votes_col]]
    voterfile_pared = voterfile_pared.groupby([county_col,voterfile_id]).sum().reset_index()
    voterfile_pared['county_voterfile_tot_vote_sum'] = voterfile_pared.groupby(county_col)[votes_col].transform('sum')
    voterfile_pared['county_voterfile_tot_vote_pct'] = voterfile_pared[votes_col]/voterfile_pared['county_voterfile_tot_vote_sum']
    voterfile_pared = voterfile_pared[~voterfile_pared['county_voterfile_tot_vote_pct'].isna()]
    return pd.Series(voterfile_pared['county_voterfile_tot_vote_pct'].values,index=voterfile_pared[voterfile_id]).to_dict()

def dist_as_voter_file_mode(voterfile_df, voterfile_id, county_col, date_col, date_lbl, votes_col, mode_col, mode_lbl):
    voterfile_pared = voterfile_df[(voterfile_df[date_col]==date_lbl)&(voterfile_df[mode_col]==mode_lbl)][[county_col,voterfile_id,votes_col]]
    voterfile_pared = voterfile_pared.groupby([county_col,voterfile_id]).sum().reset_index()
    voterfile_pared['county_voterfile_mode_sum'] = voterfile_pared.groupby(county_col)[votes_col].transform('sum')
    voterfile_pared['county_voterfile_mode_pct'] = voterfile_pared[votes_col]/voterfile_pared['county_voterfile_mode_sum']
    voterfile_pared = voterfile_pared[~voterfile_pared['county_voterfile_mode_pct'].isna()]
    return pd.Series(voterfile_pared['county_voterfile_mode_pct'].values,index=voterfile_pared[voterfile_id]).to_dict()

def dist_as_voter_file_party(voterfile_df, voterfile_id, county_col, date_col, date_lbl, votes_col, party_col, party_lbl):
    voterfile_pared = voterfile_df[(voterfile_df[date_col]==date_lbl)&(voterfile_df[party_col]==party_lbl)][[county_col,voterfile_id,votes_col]]
    voterfile_pared = voterfile_pared.groupby([county_col,voterfile_id]).sum().reset_index()
    voterfile_pared['county_voterfile_party_sum'] = voterfile_pared.groupby(county_col)[votes_col].transform('sum')
    voterfile_pared['county_voterfile_party_pct'] = voterfile_pared[votes_col]/voterfile_pared['county_voterfile_party_sum']
    voterfile_pared = voterfile_pared[~voterfile_pared['county_voterfile_party_pct'].isna()]
    return pd.Series(voterfile_pared['county_voterfile_party_pct'].values,index=voterfile_pared[voterfile_id]).to_dict()

def dist_as_voter_file_mode_and_party(voterfile_df, voterfile_id, county_col, date_col, date_lbl, votes_col, mode_col, mode_lbl, party_col, party_lbl):
    voterfile_pared = voterfile_df[(voterfile_df[date_col]==date_lbl)&(voterfile_df[mode_col]==mode_lbl)&(voterfile_df[party_col]==party_lbl)][[county_col,voterfile_id,votes_col]]
    voterfile_pared = voterfile_pared.groupby([county_col,voterfile_id]).sum().reset_index()
    voterfile_pared['county_voterfile_mode_party_sum'] = voterfile_pared.groupby(county_col)[votes_col].transform('sum')
    voterfile_pared['county_voterfile_mode_party_pct'] = voterfile_pared[votes_col]/voterfile_pared['county_voterfile_mode_party_sum']
    voterfile_pared = voterfile_pared[~voterfile_pared['county_voterfile_mode_party_pct'].isna()]
    return pd.Series(voterfile_pared['county_voterfile_mode_party_pct'].values,index=voterfile_pared[voterfile_id]).to_dict()

def dist_as_voter_file_minus_day_of(election_returns_df, election_returns_id, mode_col, day_of_label, county_col, contest_col, contest_lbl, date_col, date_lbl,votes_col, voterfile_df, voterfile_id, voterfile_county_col, voterfile_date_col, voterfile_date_lbl, voterfile_votes_col, scale = False):
    election_returns_pared = election_returns_df[(election_returns_df[contest_col]==contest_lbl)&(election_returns_df[date_col]==date_lbl)&(election_returns_df[mode_col]==day_of_label)].rename(columns = {votes_col:'Votes_day_of'})
    election_returns_pared_totals = election_returns_pared[[election_returns_id,'Votes_day_of',county_col]].groupby([election_returns_id,county_col]).sum().reset_index()
    assert(len(election_returns_pared_totals)==election_returns_pared_totals[election_returns_id].nunique())
    voterfile_pared = voterfile_df[voterfile_df[voterfile_date_col]==voterfile_date_lbl][[voterfile_county_col,voterfile_id,voterfile_votes_col]]
    voterfile_pared = voterfile_pared.groupby([voterfile_county_col,voterfile_id]).sum().reset_index()
    voterfile_pared = voterfile_pared.merge(election_returns_pared_totals[[election_returns_id,'Votes_day_of']], how = 'left', left_on = voterfile_id, right_on = election_returns_id)
    if scale:
        election_returns_all = election_returns_df[(election_returns_df[contest_col]==contest_lbl)&(election_returns_df[date_col]==date_lbl)]
        election_returns_totals = election_returns_all[[election_returns_id,votes_col,county_col]].groupby([election_returns_id,county_col]).sum().reset_index().rename(columns = {votes_col:'Vote_totals'})
        assert(len(election_returns_totals)==election_returns_totals[election_returns_id].nunique())
        voterfile_pared = voterfile_pared.merge(election_returns_totals[[election_returns_id,'Vote_totals']], how = 'left', left_on = voterfile_id, right_on = election_returns_id)
        vote_sum_scalar = (voterfile_pared['Vote_totals'].sum())/(voterfile_pared[voterfile_votes_col].sum())
        voterfile_pared[voterfile_votes_col] = voterfile_pared[voterfile_votes_col]*vote_sum_scalar
    voterfile_pared['voterfile_tot_vote_minus_day_of'] = voterfile_pared.apply(lambda x: max(0,x[voterfile_votes_col] - x['Votes_day_of']), axis = 1)
    voterfile_pared['county_voterfile_tot_vote_minus_day_of_sum'] = voterfile_pared.groupby(voterfile_county_col)['voterfile_tot_vote_minus_day_of'].transform('sum')
    voterfile_pared['county_voterfile_tot_vote_minus_day_of_pct'] = voterfile_pared['voterfile_tot_vote_minus_day_of']/voterfile_pared['county_voterfile_tot_vote_minus_day_of_sum']
    voterfile_pared = voterfile_pared[~voterfile_pared['county_voterfile_tot_vote_minus_day_of_pct'].isna()]
    return pd.Series(voterfile_pared['county_voterfile_tot_vote_minus_day_of_pct'].values,index=voterfile_pared[voterfile_id]).to_dict()

