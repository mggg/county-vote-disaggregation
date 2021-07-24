import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import geopandas as gpd
import seaborn as sns
import os
from figure_helper import *

figs_dir = "./figs/"
os.makedirs(os.path.dirname(figs_dir), exist_ok=True)

data_dir = './output_data_report/' # use './output_data/' if using generated data otherwise use './output_data_report/' to generate figures from the report

#score heatmaps
#read in file
nc_scores_filepath = data_dir+'NC_scores.csv'
ok_scores_filepath = data_dir+'OK_scores.csv'

nc_scores = pd.read_csv(nc_scores_filepath)
ok_scores = pd.read_csv(ok_scores_filepath)
comb_scores = pd.concat([nc_scores,ok_scores])
score_types = ['r2','rmse']
score_prefixes = ['counts','pct','partisan']
strategies = ['uniform', 'by_area', 'by_vap', 'by_cvap', 'by_totpop', 'by_day_of', 'by_voterfile_tot_votes', 'by_voterfile_mode', 'by_voterfile_party', 'by_voterfile_mode_party', 'by_voterfile_minus_day_of']
strategy_names_dict = {i:i.replace('day_of','election_day').upper().replace('_',' ') for i in strategies}
comb_scores['CAT'] = comb_scores.apply(lambda x: ' '.join([x['state'],str(x['year']),x['contest'],x['party'],(x['mode'] if x['mode']!= 'party' else '')]),axis=1)
comb_scores = comb_scores.sort_values('party',ascending= False).sort_values('mode',ascending= True).sort_values('year',ascending= True).sort_values('state',ascending= True)
cmap_dict = {'counts':'Oranges','pct':'Greens','partisan':'Purples'}
for score_type in score_types:
    for score_prefix in score_prefixes:
        score = score_prefix+'_'+score_type
        table_df = comb_scores[(comb_scores['strategy']!='by_scaled_voterfile_minus_day_of')][['CAT', 'strategy',score]]
        table_df = table_df.pivot('CAT','strategy',score)
        table_df = table_df.rename(columns = strategy_names_dict)
        # plt.figure(figsize = (15,10))
        # ax = sns.heatmap(table_df, annot=True, cmap = cmap_dict[score_prefix] if score_type == 'r2' else cmap_dict[score_prefix]+'_r', linewidths=1, linecolor='black',fmt=('.0f' if score_type == 'rmse' and score_prefix == 'counts' else '.2f'),annot_kws={"fontsize":14,"weight": "bold"}, vmin = 0 if score_type == 'r2' else None, vmax = 1 if score_type == 'r2' else None)
        # plt.xticks([i+.5 for i in range(len(table_df.columns))], table_df.columns, rotation=45,ha="right",fontsize=16)
        # plt.yticks([i+.5 for i in range(len(table_df.index))], table_df.index,fontsize=16)
        # plt.title(score_type+' Scores Table for '+score_prefix.upper() + ' Estimates',fontsize=16)
        # plt.xlabel('')
        # plt.ylabel('')
        # cbar = ax.collections[0].colorbar
        # cbar.ax.tick_params(labelsize=16)
        # plt.tight_layout()
        # plt.savefig(figs_dir+'_'+score+'_score_table.png')
        fig,axn = plt.subplots(2, 1, sharex=True, sharey=False,figsize = (15,10))
        sns.heatmap(table_df[table_df.index.str.contains('NC')], ax = axn[0], annot=True, cmap = cmap_dict[score_prefix] if score_type == 'r2' else cmap_dict[score_prefix]+'_r', linewidths=1, linecolor='black',fmt=('.0f' if score_type == 'rmse' and score_prefix == 'counts' else '.2f'),annot_kws={"fontsize":14,"weight": "bold"}, vmin = 0 if score_type == 'r2' else None, vmax = 1 if score_type == 'r2' else None)
        sns.heatmap(table_df[table_df.index.str.contains('OK')], ax = axn[1], annot=True, cmap = cmap_dict[score_prefix] if score_type == 'r2' else cmap_dict[score_prefix]+'_r', linewidths=1, linecolor='black',fmt=('.0f' if score_type == 'rmse' and score_prefix == 'counts' else '.2f'),annot_kws={"fontsize":14,"weight": "bold"}, vmin = 0 if score_type == 'r2' else None, vmax = 1 if score_type == 'r2' else None)
        for ax in axn.flat:    
            ax.set_xlabel('')
            ax.set_ylabel('')
            # ax.set_yticks([i+.5 for i in range(len(list(table_df[table_df.index.str.contains('NC')].index)))])
            ax.set_yticklabels(list(table_df[table_df.index.str.contains('NC')].index), fontsize= 16)
            cbar = ax.collections[0].colorbar
            cbar.ax.tick_params(labelsize=16)
        plt.xticks([i+.5 for i in range(len(table_df.columns))], table_df.columns, rotation=45,ha="right",fontsize=16)
        axn[0].set_title(score_type+' Scores Table for '+score_prefix.upper() + ' Estimates',fontsize=16)
        plt.tight_layout()
        plt.savefig(figs_dir+'_'+score+'_score_table.png')



#district estimates table/heatmap
#read in file

nc_dist_est_filepath = data_dir+'NC_2020_PRES_est_dist_votes.csv'
nc_dist_ests = pd.read_csv(nc_dist_est_filepath)
nc_dist_ests['NC_House_dist2020'] = nc_dist_ests['NC_House_dist2020'].astype('int').astype('str')
parties = ['DEM','REP']
modes = ['Early','Absentee','']
whole_county_dists = [1,5,6,13]
consistent_dists = [3,16]
inconsistent_dists = [10,11,18,20,21,33,35,37,38,43,45,56,59,62,63,71,72,74,75,76,98,103,104,105]

for col in nc_dist_ests.columns:
    if col[:3] in ['DEM','REP']:
        nc_dist_ests['pct_'+col] = nc_dist_ests[col]/(nc_dist_ests['REP'+col[3:]]+nc_dist_ests['DEM'+col[3:]])

nc_dist_ests_sample = nc_dist_ests[nc_dist_ests['NC_House_dist2020'].isin([str(i) for i in whole_county_dists+consistent_dists+inconsistent_dists])]
for party in parties:
    for mode in modes:
        table_df = nc_dist_ests_sample[['NC_House_dist2020','_'.join(['pct',party+('_'+mode if mode!='' else '')])]+['_'.join(['pct',party+('_'+mode if mode!='' else ''),strategy]) for strategy in strategies]]
        table_df = table_df.rename(columns = {'NC_House_dist2020':'House District','_'.join(['pct',party+('_'+mode if mode!='' else '')]):'Ground Truth'})
        table_df = table_df.rename(columns = {'_'.join(['pct',party+('_'+mode if mode!='' else ''),strategy]):strategy for strategy in strategies})
        table_df = table_df.rename(columns = strategy_names_dict)
        table_df = table_df.set_index('House District')
        plt.figure(figsize = (10,10))
        ax = sns.heatmap(table_df, annot=True, cmap = 'bwr_r' if party == 'DEM' else 'bwr', vmin = 0, vmax = 1, linewidths=1, linecolor='black',fmt=".1%",annot_kws={"fontsize":12,"weight": "bold"})
        plt.xticks([i+.5 for i in range(len(table_df.columns))], table_df.columns, rotation=45,ha="right", fontsize=16)
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=16)
        plt.title('District Level Percent '+party+' of Two-Way Party Share for NC '+mode+' Votes',fontsize=16)
        plt.tight_layout()
        plt.savefig(figs_dir+party+'_'+mode+'_dist_table.png')


party  = 'DEM'
mode = ''
table_df = nc_dist_ests_sample[['NC_House_dist2020','_'.join(['pct',party+('_'+mode if mode!='' else '')])]+['_'.join(['pct',party+('_'+mode if mode!='' else ''),strategy]) for strategy in strategies]]
table_df = table_df.rename(columns = {'NC_House_dist2020':'House District','_'.join(['pct',party+('_'+mode if mode!='' else '')]):'Ground Truth'})
table_df = table_df.rename(columns = {'_'.join(['pct',party+('_'+mode if mode!='' else ''),strategy]):strategy for strategy in strategies})
table_df = table_df.rename(columns = strategy_names_dict)
residual_df = table_df.copy()
for col in residual_df.columns:
    if col in strategy_names_dict.values():
        residual_df[col] = residual_df[col]-residual_df['Ground Truth']
residual_df = residual_df.drop('Ground Truth', axis =1)
residual_df = residual_df.set_index('House District')
plt.figure(figsize = (10,10))
ax = sns.heatmap(residual_df, annot=True, cmap = 'RdYlGn', vmin = -.2, vmax = .2, linewidths=1, linecolor='black',fmt=".1%",annot_kws={"fontsize":12,"weight": "bold"})
plt.xticks([i+.5 for i in range(len(residual_df.columns))], residual_df.columns, rotation=45,ha="right", fontsize=16)
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=16)
plt.title('District Level Percent DEM Residuals of Two-Way Party Share for NC Votes',fontsize=16)
plt.tight_layout()
plt.savefig(figs_dir+'DEM_RESIDUALS_dist_table.png')



#Mecklenburg County MAPS
shapefile_path = './data/NC_prec_2020'
estimates_path = data_dir+'NC_2020_PRES_est_votes.csv'
estimates_df = pd.read_csv(estimates_path)
shapefile = gpd.read_file(shapefile_path)

estimates_mec = estimates_df[estimates_df['Precinct'].str.contains('MECKLENBURG')]
shapefile_mec = shapefile[shapefile['county_nam']=='MECKLENBURG']
shapefile_mec = shapefile_mec.merge(estimates_mec, how = 'left', left_on= 'Precinct', right_on= 'Precinct')

distribution_cols = ['TOTPOP', 'TOTVAP', 'CVAP', 'AREA']+[col for col in shapefile_mec.columns if col[:3] in ['DEM','REP']]

for dist in distribution_cols:
    shapefile_mec['col_pct'] = shapefile_mec[dist]/shapefile_mec[dist].sum()
    fig,ax = plt.subplots()
    shapefile_mec.plot(column='col_pct', cmap = 'magma_r',ax = ax, edgecolor='black', linewidth = 1, vmin = 0, vmax = .036)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(figs_dir+'NC_PRES_20_MECKLENBURG_'+dist+'_map.png',dpi = 100)
    plt.close("all")


for dist in ['DEM', 'REP', 'DEM_Absentee', 'REP_Absentee', 'DEM_Early', 'REP_Early', 'DEM_In Person', 'REP_In Person']:
    shapefile_mec['col_pct'] = shapefile_mec[dist]/shapefile_mec[dist].sum()
    fig,ax = plt.subplots()
    shapefile_mec.plot(column='col_pct', cmap = 'Reds' if dist[:3]=='REP' else 'Blues',ax = ax, edgecolor='black', linewidth = 1, vmin = 0, vmax = .025)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(figs_dir+'NC_PRES_20_MECKLENBURG_party_'+dist+'_map.png',dpi = 100)
    plt.close("all")

for suffix in ['', '_Absentee', '_Early', '_In Person']:
    shapefile_mec['col_pct'] = shapefile_mec['DEM'+suffix]/(shapefile_mec['DEM'+suffix]+shapefile_mec['REP'+suffix])
    fig,ax = plt.subplots()
    shapefile_mec.plot(column='col_pct', cmap = 'seismic_r',ax = ax, edgecolor='black', linewidth = 1, vmin = 0, vmax = 1)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(figs_dir+'NC_PRES_20_MECKLENBURG_party_share'+suffix+'_map.png',dpi = 100)
    plt.close("all")

#standalone colorbars
fig = plt.figure()
ax = fig.add_axes([0.05, 0.80, 0.9, 0.05])
cb = matplotlib.colorbar.ColorbarBase(ax, orientation='horizontal', cmap=plt.get_cmap('magma_r'), norm=matplotlib.colors.Normalize(0, .036))
cb.ax.tick_params(labelsize=16)
plt.savefig(figs_dir+'MECKLENBURG_colorbar_horizontal', bbox_inches='tight')
fig = plt.figure()
ax = fig.add_axes([0.05, 0.80, 0.05, 0.9])
cb = matplotlib.colorbar.ColorbarBase(ax, orientation='vertical', cmap=plt.get_cmap('magma_r'), norm=matplotlib.colors.Normalize(0, .036))
cb.ax.tick_params(labelsize=16)
plt.savefig(figs_dir+'MECKLENBURG_colorbar_vertical', bbox_inches='tight')
fig = plt.figure()
ax = fig.add_axes([0.05, 0.80, 0.9, 0.05])
cb = matplotlib.colorbar.ColorbarBase(ax, orientation='horizontal', cmap=plt.get_cmap('seismic_r'), norm=matplotlib.colors.Normalize(0, 1))
cb.ax.tick_params(labelsize=16)
plt.savefig(figs_dir+'MECKLENBURG_colorbar_partisan_horizontal', bbox_inches='tight')
fig = plt.figure()
ax = fig.add_axes([0.05, 0.80, 0.05, 0.9])
cb = matplotlib.colorbar.ColorbarBase(ax, orientation='vertical', cmap=plt.get_cmap('seismic_r'), norm=matplotlib.colors.Normalize(0, 1))
cb.ax.tick_params(labelsize=16)
plt.savefig(figs_dir+'MECKLENBURG_colorbar_partisan_vertical', bbox_inches='tight')


#scatter plots and residual histograms
strategy1 = 'by_day_of'
strategy2 = 'by_voterfile_mode_party'
party_list = ['DEM','REP']
party = 'REP'
mode = 'Early'
scatter_max_dict = {'counts':1800, 'pct':0.15, 'partisan':1}
resid_min_max_dict = {'counts':[-1000,1000], 'pct':[-0.1,0.1], 'partisan':[-0.2,0.2]}
color_dict = {'counts':'tab:orange', 'pct':'darkgreen', 'partisan':'indigo'}

for strategy in [strategy1,strategy2]:
    counts_target = list(estimates_df[party+'_'+mode])
    counts_pred = list(estimates_df[party+'_'+mode+'_'+strategy])
    estimates_pct = estimates_df[estimates_df[party+'_'+mode+'_county']!=0]
    pct_target = list(estimates_pct[party+'_'+mode]/estimates_pct[party+'_'+mode+'_county'])
    pct_pred = list(estimates_pct[party+'_'+mode+'_'+strategy]/estimates_pct[party+'_'+mode+'_county'])
    partisan_df = estimates_df[((estimates_df[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1))!=0)&(~(estimates_df[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1)).isna())&((estimates_df[[p+'_'+mode for p in party_list]].sum(axis=1))!=0)&(~(estimates_df[[p+'_'+mode for p in party_list]].sum(axis=1)).isna())]
    partisan_target = list(partisan_df[party+'_'+mode]/(partisan_df[[p+'_'+mode for p in party_list]].sum(axis=1)))
    partisan_pred = list(partisan_df[party+'_'+mode+'_'+strategy]/(partisan_df[[p+'_'+mode+'_'+strategy for p in party_list]].sum(axis=1)))
    scatter_fig(counts_target,counts_pred,scatter_max_dict['counts'],'Actual '+party+' '+mode+' Votes','Estimated '+party+' '+mode+' Votes',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['counts'], figs_dir+'Counts_Scatterplot_'+party+'_'+mode+'_'+strategy+'.png')
    residual_fig(counts_target,counts_pred, resid_min_max_dict['counts'][0],resid_min_max_dict['counts'][1],'Residuals: '+party+' '+mode+' Votes',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['counts'], figs_dir+'Counts_Residuals_'+party+'_'+mode+'_'+strategy+'.png')
    scatter_fig(pct_target,pct_pred, scatter_max_dict['pct'],'Actual '+party+' '+mode+' Percents','Estimated '+party+' '+mode+' Percents',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['pct'], figs_dir+'PCT_Scatterplot_'+party+'_'+mode+'_'+strategy+'.png')
    residual_fig(pct_target,pct_pred, resid_min_max_dict['pct'][0],resid_min_max_dict['pct'][1],'Residuals: '+party+' '+mode+' Percents',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['pct'], figs_dir+'PCT_Residuals_'+party+'_'+mode+'_'+strategy+'.png')
    scatter_fig(partisan_target,partisan_pred, scatter_max_dict['partisan'],'Actual '+party+' '+mode+' Partisan Lean','Estimated '+party+' '+mode+' Partisan Lean',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['partisan'], figs_dir+'Partisan_Scatterplot_'+party+'_'+mode+'_'+strategy+'.png')
    residual_fig(partisan_target,partisan_pred, resid_min_max_dict['partisan'][0],resid_min_max_dict['partisan'][1],'Residuals: '+party+' '+mode+' Partisan Lean',party+' '+mode+': '+(strategy_names_dict[strategy]), party, color_dict['partisan'], figs_dir+'Partisan_Residuals_'+party+'_'+mode+'_'+strategy+'.png')


