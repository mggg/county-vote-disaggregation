import pandas as pd
import geopandas as gpd
import maup
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.colors as colors

dates = {2012:'20121106', 2014:'20141104', 2016:'20161108', 2018:'20181106', 2020:'20201103'}
voters_dfs = {}
history_dfs = {}
results_dfs = {}


for year in dates.keys():
    results_dfs[year] = pd.read_csv('./data/'+dates[year]+'_prec.csv', encoding='latin-1',quotechar='"',index_col=False)
    if year != 2020:
        results_dfs[year] = results_dfs[year].rename(columns = {'precinct_code':'precinct'})
    results_dfs[year]['CTY'] = results_dfs[year].apply(lambda x: math.floor(x['precinct']/10000), axis =1)
    results_dfs[year]['race_description'] = results_dfs[year]['race_description'].replace({'FOR UNITED STATES REPRESENTATIVE DISTRICT 02':'FOR US REPRESENTATIVE', 'FOR UNITED STATES REPRESENTATIVE DISTRICT 03':'FOR US REPRESENTATIVE', 'FOR UNITED STATES REPRESENTATIVE DISTRICT 04':'FOR US REPRESENTATIVE', 'FOR UNITED STATES REPRESENTATIVE DISTRICT 01':'FOR US REPRESENTATIVE', 'FOR UNITED STATES REPRESENTATIVE DISTRICT 05':'FOR US REPRESENTATIVE'})

cty_vr_list = []
cty_vh_list = []
for i in range(1,78):
    df_vr = pd.read_csv('./data/CTYSW_VR_20210218124038/CTY'+('00000'+str(i))[-2:]+'_vr.csv', encoding='latin-1')
    df_vr['CTY'] = i
    cty_vr_list.append(df_vr)
    df_vh = pd.read_csv('./data/CTYSW_VH_20210218124033/CTY'+('00000'+str(i))[-2:]+'_vh.csv', encoding='latin-1')
    df_vh['CTY'] = i
    cty_vh_list.append(df_vh)


vr_df = pd.concat(cty_vr_list)
vh_df = pd.concat(cty_vh_list)
vh_df = vh_df[vh_df['ElectionDate'].isin([i for i in vh_df.ElectionDate.unique() if (i.split('/')[0]=='11' and i.split('/')[-1] in ['2020','2018','2016','2014','2012'])])]
vh_df = vh_df.merge(vr_df[['VoterID','Precinct','DateOfBirth','PolitalAff']], how = 'left', left_on = 'VoterID', right_on = 'VoterID')

ey = list(vh_df['ElectionDate'])
ey_int = [int(i.split('/')[-1]) for i in ey]
by = list(vh_df['DateOfBirth'])
by_int = [int(i.split('/')[-1]) if type(i) == type('string') else i for i in by]
ed = [int(i[:-5].replace('/','')) for i in ey]
bd = [int(i[:-5].replace('/','')) if type(i) == type('string') else i for i in by]
age = [ey_int[i]-by_int[i] if (bd[i]<=ed[i] and type(by_int[i])==type(10)) else (ey_int[i]-by_int[i]-1 if type(by_int[i])==type(10) else by[i]) for i in range(len(ed))]
age_group = ['NA' if (i < 18 or type(i)!=type(10)) else ('18-25' if (i>=18 and i <= 25) else ('26-40' if (i>=26 and i <= 40) else ('41-65' if (i>=41 and i <= 65) else '66+'))) for i in age]
vh_df['age'] = age
vh_df['age_group'] = age_group
vh_df['votes'] = 1
prec_hist = vh_df[['CTY','Precinct','ElectionDate','VotingMethod','PolitalAff','age_group','votes']].groupby(['CTY','Precinct','ElectionDate','VotingMethod','PolitalAff','age_group']).count().reset_index()
prec_hist['method_group'] = prec_hist['VotingMethod'].replace({'AB':'Absentee', 'AI':'Early', 'IP':'In Person', 'MI':'Absentee', 'PI':'Absentee', 'CI':'Absentee', 'NH':'Absentee', 'EI':'Absentee', 'OV':'Absentee'})

ok = gpd.read_file('./data/OK_prec/pct_2010.shp')
ok = ok.to_crs('EPSG:2267')
ok['PCT_CEB'] = ok['PCT_CEB'].astype('int')
ok_cty = ok.dissolve(by = 'COUNTY')
ok_cong = ok.dissolve(by = 'Uscong')
ok_mggg = gpd.read_file('./data/OK_precincts_mggg/OK_precincts.shp')


ok_mggg['COUNTY'] = ok_mggg['COUNTY'].astype('int')
ok_mggg['PRECODE'] = ok_mggg['PRECODE'].astype('int')
ok_mggg['AREA'] = ok_mggg.geometry.area
ok_mggg['density'] = ok_mggg['TOTPOP']/ok_mggg['AREA']
ok_mggg['log_density'] = ok_mggg.apply(lambda x:  np.nan if x['density'] == 0 else math.log(x['density'],10),axis=1)



# plt.figure()
# ok.plot()
# plt.show()
#extra precincts in ok_mggg are splits of ok precincts
# 640007:(640007,640005)
# 640013: (640013,640009)
# 640016: (640016,640015)

# elec_dict = {2020: ['FOR CORPORATION COMMISSIONER', 'FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT', 'FOR UNITED STATES SENATOR', 'STATE QUESTION NO. 805 INITIATIVE PETITION NO. 421', 'STATE QUESTION NO. 814 LEGISLATIVE REFERENDUM NO. 375','FOR US REPRESENTATIVE'],2018: ['FOR US REPRESENTATIVE', 'FOR ATTORNEY GENERAL', 'FOR COMMISSIONER OF LABOR', 'FOR CORPORATION COMMISSIONER', 'FOR GOVERNOR', 'FOR INSURANCE COMMISSIONER', 'FOR LIEUTENANT GOVERNOR', 'FOR STATE AUDITOR AND INSPECTOR', 'FOR STATE TREASURER', 'FOR SUPERINTENDENT OF PUBLIC INSTRUCTION', 'STATE QUESTION NO. 793 INITIATIVE PETITION NO. 415', 'STATE QUESTION NO. 794 LEGISLATIVE REFERENDUM NO. 371', 'STATE QUESTION NO. 798 LEGISLATIVE REFERENDUM NO. 372', 'STATE QUESTION NO. 800 LEGISLATIVE REFERENDUM NO. 373', 'STATE QUESTION NO. 801 LEGISLATIVE REFERENDUM NO. 374'],2016: ['FOR PRESIDENT AND VICE PRESIDENT', 'FOR UNITED STATES SENATOR', 'STATE QUESTION NO. 776 LEGISLATIVE REFERENDUM NO. 367', 'STATE QUESTION NO. 777 LEGISLATIVE REFERENDUM NO. 368', 'STATE QUESTION NO. 779 INITIATIVE PETITION NO. 403', 'STATE QUESTION NO. 780 INITIATIVE PETITION NO. 404', 'STATE QUESTION NO. 781 INITIATIVE PETITION NO. 405', 'STATE QUESTION NO. 790 LEGISLATIVE REFERENDUM NO. 369', 'STATE QUESTION NO. 792 LEGISLATIVE REFERENDUM NO. 370','FOR US REPRESENTATIVE'],2014: ['FOR COMMISSIONER OF LABOR', 'FOR GOVERNOR', 'FOR LIEUTENANT GOVERNOR', 'FOR SUPERINTENDENT OF PUBLIC INSTRUCTION', 'FOR UNITED STATES SENATOR', 'FOR UNITED STATES SENATOR (UNEXPIRED TERM)', 'STATE QUESTION NO. 769 LEGISLATIVE REFERENDUM NO. 364', 'STATE QUESTION NO. 770 LEGISLATIVE REFERENDUM NO. 365', 'STATE QUESTION NO. 771 LEGISLATIVE REFERENDUM NO. 366','FOR US REPRESENTATIVE'],2012: ['FOR US REPRESENTATIVE','FOR PRESIDENT AND VICE PRESIDENT', 'STATE QUESTION NO. 758 LEGISLATIVE REFERENDUM NO. 358', 'STATE QUESTION NO. 759 LEGISLATIVE REFERENDUM NO. 359', 'STATE QUESTION NO. 762 LEGISLATIVE REFERENDUM NO. 360', 'STATE QUESTION NO. 764 LEGISLATIVE REFERENDUM NO. 361', 'STATE QUESTION NO. 765 LEGISLATIVE REFERENDUM NO. 362', 'STATE QUESTION NO. 766 LEGISLATIVE REFERENDUM NO. 363']}
elec_dict = {2020: ['FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT', 'FOR UNITED STATES SENATOR', 'FOR US REPRESENTATIVE'],2018: ['FOR US REPRESENTATIVE', 'FOR ATTORNEY GENERAL', 'FOR GOVERNOR'],2016: ['FOR PRESIDENT AND VICE PRESIDENT', 'FOR UNITED STATES SENATOR', 'FOR US REPRESENTATIVE'],2014: ['FOR GOVERNOR', 'FOR UNITED STATES SENATOR', 'FOR UNITED STATES SENATOR (UNEXPIRED TERM)', 'FOR US REPRESENTATIVE'],2012: ['FOR US REPRESENTATIVE','FOR PRESIDENT AND VICE PRESIDENT']}
elec_dict_name = {'FOR CORPORATION COMMISSIONER':'CORP_COMM', 'FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT':'PRES', 'FOR UNITED STATES SENATOR':'SEN', 'STATE QUESTION NO. 805 INITIATIVE PETITION NO. 421':'Q805', 'STATE QUESTION NO. 814 LEGISLATIVE REFERENDUM NO. 375':'Q814','FOR US REPRESENTATIVE':'USH','FOR ATTORNEY GENERAL':'AG', 'FOR COMMISSIONER OF LABOR':'COMM_LABOR', 'FOR GOVERNOR':'GOV', 'FOR INSURANCE COMMISSIONER':'INS_COMM', 'FOR LIEUTENANT GOVERNOR':'LGOV', 'FOR STATE AUDITOR AND INSPECTOR':'AUD', 'FOR STATE TREASURER':'TRES', 'FOR SUPERINTENDENT OF PUBLIC INSTRUCTION':'SUP_PI', 'STATE QUESTION NO. 793 INITIATIVE PETITION NO. 415':'Q793', 'STATE QUESTION NO. 794 LEGISLATIVE REFERENDUM NO. 371':'Q794', 'STATE QUESTION NO. 798 LEGISLATIVE REFERENDUM NO. 372':'Q798', 'STATE QUESTION NO. 800 LEGISLATIVE REFERENDUM NO. 373':'Q800', 'STATE QUESTION NO. 801 LEGISLATIVE REFERENDUM NO. 374':'Q801','FOR PRESIDENT AND VICE PRESIDENT':'PRES', 'STATE QUESTION NO. 776 LEGISLATIVE REFERENDUM NO. 367':'Q776', 'STATE QUESTION NO. 777 LEGISLATIVE REFERENDUM NO. 368':'Q777', 'STATE QUESTION NO. 779 INITIATIVE PETITION NO. 403':'Q779', 'STATE QUESTION NO. 780 INITIATIVE PETITION NO. 404':'Q780', 'STATE QUESTION NO. 781 INITIATIVE PETITION NO. 405':'Q781', 'STATE QUESTION NO. 790 LEGISLATIVE REFERENDUM NO. 369':'Q790', 'STATE QUESTION NO. 792 LEGISLATIVE REFERENDUM NO. 370':'Q791','FOR UNITED STATES SENATOR (UNEXPIRED TERM)':'SEN_unexpired', 'STATE QUESTION NO. 769 LEGISLATIVE REFERENDUM NO. 364':'Q769', 'STATE QUESTION NO. 770 LEGISLATIVE REFERENDUM NO. 365':'Q770', 'STATE QUESTION NO. 771 LEGISLATIVE REFERENDUM NO. 366':'Q771','STATE QUESTION NO. 758 LEGISLATIVE REFERENDUM NO. 358':'Q758', 'STATE QUESTION NO. 759 LEGISLATIVE REFERENDUM NO. 359':'Q759', 'STATE QUESTION NO. 762 LEGISLATIVE REFERENDUM NO. 360':'Q762', 'STATE QUESTION NO. 764 LEGISLATIVE REFERENDUM NO. 361':'Q764', 'STATE QUESTION NO. 765 LEGISLATIVE REFERENDUM NO. 362':'Q765', 'STATE QUESTION NO. 766 LEGISLATIVE REFERENDUM NO. 363':'Q766'}

for year in dates.keys():
    print(year)
    results_dfs[year] = results_dfs[year][results_dfs[year]['race_description'].isin(elec_dict[year])]
    results_dfs[year]['tot_votes_cty_pct'] = results_dfs[year]['cand_tot_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_tot_votes'].transform('sum')
    results_dfs[year]['elecday_votes_cty_pct'] = results_dfs[year]['cand_elecday_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_elecday_votes'].transform('sum')
    results_dfs[year]['early_votes_cty_pct'] = results_dfs[year]['cand_early_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_early_votes'].transform('sum')
    results_dfs[year]['absmail_votes_cty_pct'] = results_dfs[year]['cand_absmail_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_absmail_votes'].transform('sum')

cmap_dict = {'REP':'Reds', 'LIB':'Purples', 'DEM':'Blues', 'IND':'Greens','NO':'Reds','YES':'Blues'}

# #precinct level distirbution maps of vote method across county
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][results_dfs[year]['race_description'] == elec]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         for cand in elec_df['cand_name'].unique():
#             cand_df = elec_df[elec_df['cand_name'] == cand]
#             assert(len(cand_df['cand_party'].unique()) == 1)
#             choice = list(cand_df['cand_party'].unique())[0]
#             if pd.isnull(choice):
#                 choice = cand.split(' ')[-1]            
#             ok_plot = ok.merge(cand_df[['precinct','tot_votes_cty_pct','elecday_votes_cty_pct','early_votes_cty_pct','absmail_votes_cty_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
#             for vote_dist in ['tot_votes_cty_pct','elecday_votes_cty_pct','early_votes_cty_pct','absmail_votes_cty_pct']:
#                 fig, ax = plt.subplots()
#                 ok_plot.plot(column = vote_dist,cmap = cmap_dict[choice],ax=ax, vmin= 0, vmax = 1)
#                 ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#                 if elec == 'FOR US REPRESENTATIVE':
#                     ok_cong.geometry.boundary.plot(color=None,edgecolor='lightgray',linewidth = 3,alpha = .5, ax=ax)
#                 ax.set_axis_off()
#                 plt.title(str(year) + ' ' +elec + '\n'+cand)
#                 plt.tight_layout()
#                 plt.savefig('./figs/county_percent/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_dist+'.png')
#                 plt.close('all')


# #precinct level maps of vote method distributions
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][results_dfs[year]['race_description'] == elec]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         for cand in elec_df['cand_name'].unique():
#             cand_df = elec_df[elec_df['cand_name'] == cand]
#             assert(len(cand_df['cand_party'].unique()) == 1)
#             choice = list(cand_df['cand_party'].unique())[0]
#             if pd.isnull(choice):
#                 choice = cand.split(' ')[-1]            
#             ok_plot = ok.merge(cand_df[['precinct','cand_tot_votes','cand_elecday_votes','cand_early_votes','cand_absmail_votes']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
#             for vote_type in ['cand_early_votes','cand_elecday_votes','cand_absmail_votes']:
#                 fig, ax = plt.subplots()
#                 ok_plot.plot(column = (ok_plot[vote_type]/ok_plot['cand_tot_votes']),cmap = cmap_dict[choice],ax=ax, vmin= 0, vmax = 1)
#                 ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#                 if elec == 'FOR US REPRESENTATIVE':
#                     ok_cong.geometry.boundary.plot(color=None,edgecolor='lightgray',linewidth = 3,alpha = .5, ax=ax)
#                 ax.set_axis_off()
#                 plt.title(str(year) + ' ' +elec + '\n'+cand)
#                 plt.tight_layout()
#                 plt.savefig('./figs/prec_percent/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_prec.png')
#                 plt.close('all')



# #precinct level maps of results pct
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][results_dfs[year]['race_description'] == elec]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         elec_df['prec_vote_sum'] = elec_df.groupby(['precinct'])['cand_tot_votes'].transform('sum')
#         for cand in elec_df['cand_name'].unique():
#             cand_df = elec_df[elec_df['cand_name'] == cand]
#             assert(len(cand_df['cand_party'].unique()) == 1)
#             choice = list(cand_df['cand_party'].unique())[0]
#             if pd.isnull(choice):
#                 choice = cand.split(' ')[-1]            
#             ok_plot = ok.merge(cand_df[['precinct','cand_tot_votes','prec_vote_sum']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = (ok_plot['cand_tot_votes']/ok_plot['prec_vote_sum']),cmap = cmap_dict[choice],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             if elec == 'FOR US REPRESENTATIVE':
#                 ok_cong.geometry.boundary.plot(color=None,edgecolor='lightgray',linewidth = 3,alpha = .5, ax=ax)
#             ax.set_axis_off()
#             plt.title(str(year) + ' ' +elec + '\n'+cand)
#             plt.tight_layout()
#             plt.savefig('./figs/prec_percent/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_tot_prec.png')
#             plt.close('all')
#         #two-way vote share
#         two_party_elec_df = elec_df[elec_df['cand_party'].isin(['REP','DEM'])]
#         if len(two_party_elec_df) >= 0:
#             two_party_elec_df = two_party_elec_df.groupby(['precinct','cand_party']).sum().reset_index()
#             two_party_elec_df['prec_vote_sum'] = two_party_elec_df.groupby(['precinct'])['cand_tot_votes'].transform('sum')
#             REP_df = two_party_elec_df[two_party_elec_df['cand_party'] == 'REP']
#             assert(len(REP_df) == two_party_elec_df.precinct.nunique())
#             ok_plot = ok.merge(REP_df[['precinct','cand_tot_votes','prec_vote_sum']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = (ok_plot['cand_tot_votes']/ok_plot['prec_vote_sum']),cmap = 'seismic',ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             if elec == 'FOR US REPRESENTATIVE':
#                 ok_cong.geometry.boundary.plot(color=None,edgecolor='lightgray',linewidth = 3,alpha = .5, ax=ax)
#             ax.set_axis_off()
#             plt.title(str(year) + ' ' +elec + '\n%REP')
#             plt.tight_layout()
#             plt.savefig('./figs/prec_percent/'+str(year)+'_'+elec_dict_name[elec]+'_pct_REP_prec.png')
#             plt.close('all')



# #precinct level maps of method pct
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][results_dfs[year]['race_description'] == elec]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         prec_df = elec_df.groupby(['precinct']).sum().reset_index()
#         assert(len(prec_df) == elec_df.precinct.nunique())
#         ok_plot = ok.merge(cand_df[['precinct','cand_tot_votes','cand_elecday_votes','cand_early_votes','cand_absmail_votes']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
#         for vote_type in ['cand_early_votes','cand_elecday_votes','cand_absmail_votes']:
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = (ok_plot[vote_type]/ok_plot['cand_tot_votes']),cmap = cmap_dict[choice],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             if elec == 'FOR US REPRESENTATIVE':
#                 ok_cong.geometry.boundary.plot(color=None,edgecolor='lightgray',linewidth = 3,alpha = .5, ax=ax)
#             ax.set_axis_off()
#             plt.title(str(year) + ' ' +elec + '\n'+vote_type)
#             plt.tight_layout()
#             plt.savefig('./figs/prec_percent/'+str(year)+'_'+elec_dict_name[elec]+'_'+vote_type+'_method_prec.png')
#             plt.close('all')


# #maps of registration distribution across precincts
# for date in prec_hist.ElectionDate.unique():
#     elec_hist = prec_hist[prec_hist['ElectionDate']==date]
#     df_age = elec_hist.groupby(['age_group','Precinct']).sum().reset_index()
#     df_age['prec_sum'] = df_age.groupby(['Precinct'])['votes'].transform('sum')
#     df_age['age_pct'] = df_age['votes']/df_age['prec_sum']
#     for ag in df_age.age_group.unique():
#         df_age_group = df_age[df_age['age_group']==ag]
#         assert(df_age_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_age_group[['Precinct','age_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'age_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' voters aged: ' +ag)
#         plt.tight_layout()
#         plt.savefig('./figs/prec_percent/age_'+str(ag)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     df_parties = elec_hist.groupby(['PolitalAff','Precinct']).sum().reset_index()
#     df_parties['prec_sum'] = df_parties.groupby(['Precinct'])['votes'].transform('sum')
#     df_parties['party_pct'] = df_parties['votes']/df_parties['prec_sum']
#     for party in df_parties.PolitalAff.unique():
#         df_party = df_parties[df_parties['PolitalAff']==party]
#         assert(df_party.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_party[['Precinct','party_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'party_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+party+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/prec_percent/party_'+str(party)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     df_methods = elec_hist[elec_hist['VotingMethod'].isin(['AB','MI','OV','NH','PI','CI','EI'])]
#     df_methods['VotingMethod'] = df_methods['VotingMethod'].replace({'PI':'I','CI':'I','EI':'I'})
#     df_methods = df_methods.groupby(['VotingMethod','Precinct']).sum().reset_index()
#     df_methods['prec_sum'] = df_methods.groupby(['Precinct'])['votes'].transform('sum')
#     df_methods['abs_method_pct'] = df_methods['votes']/df_methods['prec_sum']
#     for method in df_methods.VotingMethod.unique():
#         df_method = df_methods[df_methods['VotingMethod']==method]
#         assert(df_method.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_method[['Precinct','abs_method_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'abs_method_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+method+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/prec_percent/abs_method_'+str(method)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     df_method_groups = elec_hist[elec_hist['method_group'].isin(['Absentee', 'Early', 'In Person'])]
#     df_method_groups = df_method_groups.groupby(['method_group','Precinct']).sum().reset_index()
#     df_method_groups['prec_sum'] = df_method_groups.groupby(['Precinct'])['votes'].transform('sum')
#     df_method_groups['method_group_pct'] = df_method_groups['votes']/df_method_groups['prec_sum']
#     for method_group in df_method_groups.method_group.unique():
#         df_method_group = df_method_groups[df_method_groups['method_group']==method_group]
#         assert(df_method_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_method_group[['Precinct','method_group_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'method_group_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+method_group+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/prec_percent/method_group_'+str(method_group)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     for party in elec_hist.PolitalAff.unique():
#         df_party_method_groups = elec_hist[(elec_hist['method_group'].isin(['Absentee', 'Early', 'In Person']))&(elec_hist['PolitalAff']==party)]
#         df_party_method_groups = df_party_method_groups.groupby(['method_group','Precinct']).sum().reset_index()
#         df_party_method_groups['prec_sum'] = df_party_method_groups.groupby(['Precinct'])['votes'].transform('sum')
#         df_party_method_groups['method_group_pct'] = df_party_method_groups['votes']/df_party_method_groups['prec_sum']
#         for method_group in df_party_method_groups.method_group.unique():
#             df_party_method_group = df_party_method_groups[df_party_method_groups['method_group']==method_group]
#             assert(df_party_method_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#             ok_plot = ok.merge(df_party_method_group[['Precinct','method_group_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = 'method_group_pct',cmap = cmap_dict[party],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             ax.set_axis_off()
#             plt.title(str(date) + ' '+method_group+ ' voters')
#             plt.tight_layout()
#             plt.savefig('./figs/prec_percent/party_method_group_'+str(party)+'_'+str(method_group)+'_'+date.split('/')[-1]+'_prec.png')
#             plt.close('all')    
#         df_age = elec_hist[elec_hist['PolitalAff']==party].groupby(['age_group','Precinct']).sum().reset_index()
#         df_age['prec_sum'] = df_age.groupby(['Precinct'])['votes'].transform('sum')
#         df_age['age_pct'] = df_age['votes']/df_age['prec_sum']
#         for ag in df_age.age_group.unique():
#             df_age_group = df_age[df_age['age_group']==ag]
#             assert(df_age_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#             ok_plot = ok.merge(df_age_group[['Precinct','age_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = 'age_pct',cmap = cmap_dict[party],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             ax.set_axis_off()
#             plt.title(str(date) + ' voters aged: ' +ag)
#             plt.tight_layout()
#             plt.savefig('./figs/prec_percent/party_age_'+str(party)+'_'+str(ag)+'_'+date.split('/')[-1]+'_prec.png')
#             plt.close('all')





for year in dates.keys():
    print(year)
    results_dfs[year] = results_dfs[year][results_dfs[year]['race_description'].isin(elec_dict[year])]
    results_dfs[year]['tot_votes_cty_pct'] = results_dfs[year]['cand_tot_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_tot_votes'].transform('sum')
    results_dfs[year]['elecday_votes_cty_pct'] = results_dfs[year]['cand_elecday_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_elecday_votes'].transform('sum')
    results_dfs[year]['early_votes_cty_pct'] = results_dfs[year]['cand_early_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_early_votes'].transform('sum')
    results_dfs[year]['absmail_votes_cty_pct'] = results_dfs[year]['cand_absmail_votes']/results_dfs[year].groupby(['CTY','cand_name'])['cand_absmail_votes'].transform('sum')



# #maps of registration distribution across counties
# for date in prec_hist.ElectionDate.unique():
#     elec_hist = prec_hist[prec_hist['ElectionDate']==date]
#     df_age = elec_hist.groupby(['age_group','Precinct','CTY']).sum().reset_index()
#     df_age['county_sum'] = df_age.groupby(['age_group','CTY'])['votes'].transform('sum')
#     df_age['age_pct'] = df_age['votes']/df_age['county_sum']
#     for ag in df_age.age_group.unique():
#         df_age_group = df_age[df_age['age_group']==ag]
#         assert(df_age_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_age_group[['Precinct','age_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'age_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' voters aged: ' +ag)
#         plt.tight_layout()
#         plt.savefig('./figs/county_percent/age_'+str(ag)+'_'+date.split('/')[-1]+'_cty_pct.png')
#         plt.close('all')
#     df_parties = elec_hist.groupby(['PolitalAff','Precinct','CTY']).sum().reset_index()
#     df_parties['county_sum'] = df_parties.groupby(['PolitalAff','CTY'])['votes'].transform('sum')
#     df_parties['party_pct'] = df_parties['votes']/df_parties['county_sum']
#     for party in df_parties.PolitalAff.unique():
#         df_party = df_parties[df_parties['PolitalAff']==party]
#         assert(df_party.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_party[['Precinct','party_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'party_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+party+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/county_percent/party_'+str(party)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     df_methods = elec_hist[elec_hist['VotingMethod'].isin(['AB','MI','OV','NH','PI','CI','EI'])]
#     df_methods['VotingMethod'] = df_methods['VotingMethod'].replace({'PI':'I','CI':'I','EI':'I'})
#     df_methods = df_methods.groupby(['VotingMethod','Precinct','CTY']).sum().reset_index()
#     df_methods['county_sum'] = df_methods.groupby(['VotingMethod','CTY'])['votes'].transform('sum')
#     df_methods['abs_method_pct'] = df_methods['votes']/df_methods['county_sum']
#     for method in df_methods.VotingMethod.unique():
#         df_method = df_methods[df_methods['VotingMethod']==method]
#         assert(df_method.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_method[['Precinct','abs_method_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'abs_method_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+method+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/county_percent/abs_method_'+str(method)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     df_method_groups = elec_hist[elec_hist['method_group'].isin(['Absentee', 'Early', 'In Person'])]
#     df_method_groups = df_method_groups.groupby(['method_group','Precinct','CTY']).sum().reset_index()
#     df_method_groups['county_sum'] = df_method_groups.groupby(['method_group','CTY'])['votes'].transform('sum')
#     df_method_groups['method_group_pct'] = df_method_groups['votes']/df_method_groups['county_sum']
#     for method_group in df_method_groups.method_group.unique():
#         df_method_group = df_method_groups[df_method_groups['method_group']==method_group]
#         assert(df_method_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#         ok_plot = ok.merge(df_method_group[['Precinct','method_group_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#         fig, ax = plt.subplots()
#         ok_plot.plot(column = 'method_group_pct',cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#         ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#         ax.set_axis_off()
#         plt.title(str(date) + ' '+method_group+ ' voters')
#         plt.tight_layout()
#         plt.savefig('./figs/county_percent/method_group_'+str(method_group)+'_'+date.split('/')[-1]+'_prec.png')
#         plt.close('all')
#     for party in elec_hist.PolitalAff.unique():
#         df_party_method_groups = elec_hist[(elec_hist['method_group'].isin(['Absentee', 'Early', 'In Person']))&(elec_hist['PolitalAff']==party)]
#         df_party_method_groups = df_party_method_groups.groupby(['method_group','Precinct','CTY']).sum().reset_index()
#         df_party_method_groups['county_sum'] = df_party_method_groups.groupby(['method_group','CTY'])['votes'].transform('sum')
#         df_party_method_groups['method_group_pct'] = df_party_method_groups['votes']/df_party_method_groups['county_sum']
#         for method_group in df_party_method_groups.method_group.unique():
#             df_party_method_group = df_party_method_groups[df_party_method_groups['method_group']==method_group]
#             assert(df_party_method_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#             ok_plot = ok.merge(df_party_method_group[['Precinct','method_group_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = 'method_group_pct',cmap = cmap_dict[party],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             ax.set_axis_off()
#             plt.title(str(date) + ' '+method_group+ ' voters')
#             plt.tight_layout()
#             plt.savefig('./figs/county_percent/party_method_group_'+str(party)+'_'+str(method_group)+'_'+date.split('/')[-1]+'_prec.png')
#             plt.close('all')    
#         df_age = elec_hist[elec_hist['PolitalAff']==party].groupby(['age_group','Precinct','CTY']).sum().reset_index()
#         df_age['county_sum'] = df_age.groupby(['age_group','CTY'])['votes'].transform('sum')
#         df_age['age_pct'] = df_age['votes']/df_age['county_sum']
#         for ag in df_age.age_group.unique():
#             df_age_group = df_age[df_age['age_group']==ag]
#             assert(df_age_group.groupby('Precinct').count().reset_index()['CTY'].max()==1)
#             ok_plot = ok.merge(df_age_group[['Precinct','age_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'Precinct')
#             fig, ax = plt.subplots()
#             ok_plot.plot(column = 'age_pct',cmap = cmap_dict[party],ax=ax, vmin= 0, vmax = 1)
#             ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#             ax.set_axis_off()
#             plt.title(str(date) + ' voters aged: ' +ag)
#             plt.tight_layout()
#             plt.savefig('./figs/county_percent/party_age_'+str(party)+'_'+str(ag)+'_'+date.split('/')[-1]+'_prec.png')
#             plt.close('all')




# #race choropleths
# for vap_group in ['HVAP', 'WVAP', 'BVAP', 'AMINVAP']:
#     fig, ax = plt.subplots()
#     ok_mggg.plot(column = ok_mggg[vap_group]/ok_mggg['VAP'],cmap = 'Reds',ax=ax, vmin= 0, vmax = 1)
#     ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#     ax.set_axis_off()
#     plt.title('Distribution of '+vap_group)
#     plt.tight_layout()
#     plt.savefig('./figs/demog_maps/'+vap_group+'_dist.png')
#     plt.close('all')

# fig, ax = plt.subplots()
# ok_mggg.plot(column = ok_mggg['VAP'],cmap = 'Reds',ax=ax)
# ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
# ax.set_axis_off()
# plt.title('Distribution of VAP')
# plt.tight_layout()
# plt.savefig('./figs/demog_maps/VAP_dist.png', dpi = 300)
# plt.close('all')






# #bar charts comparing methods, outcomes, method by outcome, outcome by method
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][results_dfs[year]['race_description'] == elec]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         cand_df = elec_df[['cand_party','cand_absmail_votes','cand_early_votes', 'cand_elecday_votes', 'cand_tot_votes']].groupby(['cand_party']).sum().reset_index()
#         cand_df = cand_df[cand_df['cand_party'].isin(['DEM','REP'])]
#         # fig, ax = plt.subplots()
#         # cand_df[['cand_party','cand_tot_votes']].plot.bar(x = 'cand_party',ax=ax,legend=False)
#         # plt.title(str(year) +' '+ str(elec) +'\nDistribution of Votes by Party')
#         # plt.ylabel("Number of Voters")
#         # plt.tight_layout()
#         # plt.savefig('./figs/statewide_party_dist'+str(year)+'_'+elec_dict_name[elec]+'.png')
#         # plt.close('all')
#         # fig, ax = plt.subplots()
#         # cand_df[['cand_absmail_votes','cand_early_votes', 'cand_elecday_votes']].rename(columns ={'cand_absmail_votes':'By Mail','cand_early_votes':'Early', 'cand_elecday_votes':'Day Of'}).sum().reset_index().plot.bar(x = 'index',ax=ax,legend=False)
#         # plt.title(str(year) +' '+ str(elec) +'\nDistribution of Votes by Method')
#         # plt.ylabel("Number of Voters")
#         # plt.xlabel("Method")
#         # plt.tight_layout()
#         # plt.savefig('./figs/statewide_method_dist'+str(year)+'_'+elec_dict_name[elec]+'.png')
#         # plt.close('all')        
#         # fig, ax = plt.subplots()
#         # cand_df[['cand_absmail_votes','cand_early_votes', 'cand_elecday_votes','cand_tot_votes']].rename(columns ={'cand_absmail_votes':'By Mail','cand_early_votes':'Early', 'cand_elecday_votes':'Day Of','cand_tot_votes':'Total'}).plot.bar(x = 'cand_party',ax=ax)
#         # plt.title(str(year) +' '+ str(elec) +'\nDistribution of Votes by Method')
#         # plt.ylabel("Number of Voters")
#         # plt.xlabel("Party")
#         # plt.tight_layout()
#         # plt.savefig('./figs/statewide_method_dist'+str(year)+'_'+elec_dict_name[elec]+'.png')
#         # plt.close('all')        
#         fig, ax = plt.subplots()
#         cand_df[['cand_party','cand_absmail_votes','cand_early_votes', 'cand_elecday_votes','cand_tot_votes']].rename(columns ={'cand_absmail_votes':'By Mail','cand_early_votes':'Early', 'cand_elecday_votes':'Day Of','cand_tot_votes':'Total'}).plot.bar(x = 'cand_party',ax=ax)
#         plt.title(str(year) +' '+ str(elec) +'\nDistribution of Method Votes by Party')
#         plt.ylabel("Number of Voters")
#         plt.xlabel("Party")
#         plt.tight_layout()
#         plt.savefig('./figs/statewide_method_party_dist'+str(year)+'_'+elec_dict_name[elec]+'.png')
#         plt.close('all')        
#         fig, ax = plt.subplots()
#         cand_df[['cand_party','cand_absmail_votes','cand_early_votes', 'cand_elecday_votes','cand_tot_votes']].rename(columns ={'cand_absmail_votes':'By Mail','cand_early_votes':'Early', 'cand_elecday_votes':'Day Of','cand_tot_votes':'Total'}).set_index('cand_party').transpose().reset_index().plot.bar(x = 'index',ax=ax)
#         plt.title(str(year) +' '+ str(elec) +'\nDistribution of Party Votes by Method')
#         plt.ylabel("Number of Voters")
#         plt.xlabel("Method")
#         plt.tight_layout()
#         plt.savefig('./figs/statewide_party_method_dist'+str(year)+'_'+elec_dict_name[elec]+'.png')
#         plt.close('all')        

# #bar charts comparing age, party, method, method by party, age by party, method by age, party by age, party by method, age by method, method by age and party, party by method and age, age by method and party
# for date in prec_hist.ElectionDate.unique():
#     elec_hist = prec_hist[prec_hist['ElectionDate']==date]
#     elec_hist = elec_hist[(elec_hist['PolitalAff'].isin(['DEM', 'IND', 'REP']))&(elec_hist['age_group'].isin(['26-40', '41-65', '66+', '18-25']))&(elec_hist['method_group'].isin(['Absentee', 'Early', 'In Person']))]
#     # party_age = elec_hist[['PolitalAff','age_group','votes']].groupby(['PolitalAff','age_group']).sum().reset_index()
#     # fig, ax = plt.subplots()
#     # df = party_age.pivot(columns = 'PolitalAff', values = 'votes', index = 'age_group').reset_index()
#     # df.append({**{'age_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'age_group'}},ignore_index=True).plot.bar(x = 'age_group',ax=ax)
#     # plt.title(str(date)+' Distribution of Party Votes by Age Group')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Age Group")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_party_age_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')        
#     # fig, ax = plt.subplots()
#     # df = party_age.pivot(columns = 'age_group', values = 'votes', index = 'PolitalAff').reset_index()
#     # df.append({**{'PolitalAff':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'PolitalAff'}},ignore_index=True).plot.bar(x = 'PolitalAff',ax=ax)
#     # plt.title(str(date)+' Distribution of Age Group Votes by Party')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Party")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_age_party_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')        
#     # method_age = elec_hist[['method_group','age_group','votes']].groupby(['method_group','age_group']).sum().reset_index()
#     # fig, ax = plt.subplots()
#     # df = method_age.pivot(columns = 'age_group', values = 'votes', index = 'method_group').reset_index()
#     # df.append({**{'method_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'method_group'}},ignore_index=True).plot.bar(x = 'method_group',ax=ax)
#     # plt.title(str(date)+' Distribution of Age Group Votes by Method')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Method")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_age_method_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')        
#     # fig, ax = plt.subplots()
#     # df = method_age.pivot(columns = 'method_group', values = 'votes', index = 'age_group').reset_index()
#     # df.append({**{'age_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'age_group'}},ignore_index=True).plot.bar(x = 'age_group',ax=ax)
#     # plt.title(str(date)+' Distribution of Method Votes by Age Group')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Age Group")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_method_age_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')
#     # method_party = elec_hist[['method_group','PolitalAff','votes']].groupby(['method_group','PolitalAff']).sum().reset_index()
#     # fig, ax = plt.subplots()
#     # df = method_party.pivot(columns = 'PolitalAff', values = 'votes', index = 'method_group').reset_index()
#     # df.append({**{'method_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'method_group'}},ignore_index=True).plot.bar(x = 'method_group',ax=ax)
#     # plt.title(str(date)+' Distribution of Party Votes by Method')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Method")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_party_method_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')        
#     # fig, ax = plt.subplots()
#     # df = method_party.pivot(columns = 'method_group', values = 'votes', index = 'PolitalAff').reset_index()
#     # df.append({**{'PolitalAff':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'PolitalAff'}},ignore_index=True).plot.bar(x = 'PolitalAff',ax=ax)
#     # plt.title(str(date)+' Distribution of Method Votes by Party')
#     # plt.ylabel("Number of Voters")
#     # plt.xlabel("Party")
#     # plt.tight_layout()
#     # plt.savefig('./figs/bar_plots/statewide_history_method_party_dist'+str(date).split('/')[-1]+'_.png')
#     # plt.close('all')
#     for party in ['DEM','REP']:
#         method_age = elec_hist[elec_hist['PolitalAff']==party][['method_group','age_group','votes']].groupby(['method_group','age_group']).sum().reset_index()
#         fig, ax = plt.subplots()
#         df = method_age.pivot(columns = 'age_group', values = 'votes', index = 'method_group').reset_index()
#         df.append({**{'method_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'method_group'}},ignore_index=True).plot.bar(x = 'method_group',ax=ax)
#         plt.title(str(date)+' '+party+' Distribution of Age Group Votes by Method')
#         plt.ylabel("Number of Voters")
#         plt.xlabel("Method")
#         # plt.ylim(0,450000)
#         plt.tight_layout()
#         plt.savefig('./figs/bar_plots/statewide_history_age_method_dist_'+party+'_'+str(date).split('/')[-1]+'_.png')
#         plt.close('all')        
#         fig, ax = plt.subplots()
#         df = method_age.pivot(columns = 'method_group', values = 'votes', index = 'age_group').reset_index()
#         df.append({**{'age_group':'TOTAL'}, **{col:df[col].sum() for col in df.columns if col != 'age_group'}},ignore_index=True).plot.bar(x = 'age_group',ax=ax)
#         plt.title(str(date)+' '+party+' Distribution of Method Votes by Age Group')
#         plt.ylabel("Number of Voters")
#         plt.xlabel("Age Group")
#         # plt.ylim(0,700000)
#         plt.tight_layout()
#         plt.savefig('./figs/bar_plots/statewide_history_method_age_dist_'+party+'_'+str(date).split('/')[-1]+'_.png')
#         plt.close('all')

#scatterplot comparing early/mail in votes to: day-of votes, registered voters party dist, actual voters party dist, actual voters party dist minus day-of, method voters by party?
color_dict = {'all':'tab:gray','REP':'tab:red','DEM':'tab:blue','IND':'tab:green','LIB':'tab:purple'}

def scatter_fig(df,choice, vote_type, ground_truth_col, county_sum_col, estimate_dist_col,max_x_y, estimate_name,fig_name):
    fig, ax = plt.subplots()
    plt.scatter(df[ground_truth_col],df[county_sum_col]*df[estimate_dist_col], alpha = .3, s = 10, zorder = 1, c = color_dict[choice])
    max_val = max(df[ground_truth_col].quantile(max_x_y),(df[county_sum_col]*df[estimate_dist_col]).quantile(max_x_y))
    plt.plot([0,max_val],[0,max_val], color = 'k',zorder=2)
    plt.xlabel('Actual '+vote_type +' Votes')
    plt.ylabel('Votes predicted by \n'+ estimate_name)
    plt.xlim(0,max_val)
    plt.ylim(0,max_val)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

def error_fig(df,choice, vote_type, ground_truth_col, county_sum_col, estimate_dist_col, votes_lb, estimate_name,fig_name):
    fig, ax = plt.subplots()
    df['diff_pct'] =  ((df[county_sum_col]*df[estimate_dist_col])-df[ground_truth_col])/df[ground_truth_col]
    plt.hist(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'], bins = [i/20 -1 for i in range(225)]+ [max(11,df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].max()+1)], color = color_dict[choice])
    plt.xlabel('Difference ('+estimate_name+' - '+vote_type +')\nas Percent of True Value \n mean: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].mean(),3))+', sd: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].std(),3))+'\n filtered mean: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)&(df[ground_truth_col]>votes_lb)]['diff_pct'].mean(),3))+', filtered sd: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)&(df[ground_truth_col]>votes_lb)]['diff_pct'].std(),3)))
    plt.ylabel('Frequency')
    plt.axvline(x = df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].mean(), color = 'k', lw = 2,alpha = .8, zorder = 2)
    plt.xlim(-1.05,10.05)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

def error_map(df,gdf, ground_truth_col, county_sum_col, estimate_dist_col, votes_lb,fig_name):
    df['diff_pct'] =  ((df[county_sum_col]*df[estimate_dist_col])-df[ground_truth_col])/df[ground_truth_col]
    ok_plot = gdf.merge(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)&(df[ground_truth_col]>votes_lb)][['precinct','diff_pct']], how = 'left', left_on = 'PCT_CEB', right_on = 'precinct')
    fig, ax = plt.subplots()
    norm = colors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=2)
    if len(ok_plot[~ok_plot['diff_pct'].isna()]) > 0:
        ok_plot.plot(column = 'diff_pct',cmap = 'bwr_r',ax=ax, norm=norm,missing_kwds= dict(color = "gray"))
    else:
        ok_plot.plot(color= 'gray')
    ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

def error_correlation(df1,df2, join1, join2,comp_col, choice, vote_type, ground_truth_col, county_sum_col, estimate_dist_col, votes_lb, estimate_name,fig_name):
    fig, ax = plt.subplots(2,1)
    df1['diff_pct'] = ((df1[county_sum_col]*df1[estimate_dist_col])-df1[ground_truth_col])/df1[ground_truth_col]
    df1 = df1.merge(df2[[comp_col, join2]], how = 'left', left_on = join1, right_on = join2)
    df1 = df1[(df1['diff_pct']< math.inf)&(df1['diff_pct']>-1*math.inf)]
    ax[0].scatter(df1[df1[ground_truth_col]>=votes_lb][comp_col],df1[df1[ground_truth_col]>=votes_lb]['diff_pct'],alpha = .2, color = color_dict[choice], label = 'Counts ≥ '+str(votes_lb))
    ax[1].scatter(df1[df1[ground_truth_col]<votes_lb][comp_col],df1[df1[ground_truth_col]<votes_lb]['diff_pct'],alpha = .2, color = 'gray', label = 'Counts < '+str(votes_lb))
    plt.xlabel(comp_col)
    plt.ylabel('Percent Difference')
    ax[0].set_xlim(0-.05*df1[comp_col].max(),df1[comp_col].max()*1.05)
    ax[1].set_xlim(0-.05*df1[comp_col].max(),df1[comp_col].max()*1.05)
    ax[0].set_ylim(-1.05,10.05)
    ax[1].set_ylim(-1.05,10.05)
    ax[0].legend()
    ax[1].legend()
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')


def partisan_scatter(df,ground_truth_col_R, ground_truth_col_D, est_R, est_D, estimate_name,fig_name):
    fig, ax = plt.subplots()
    plt.scatter(df[ground_truth_col_D]/(df[ground_truth_col_D]+df[ground_truth_col_R]),df[est_D]/(df[est_D]+df[est_R]), alpha = .3, s = 10, zorder = 1, c = 'tab:purple')
    plt.plot([0,1],[0,1], color = 'k',zorder=0)
    plt.xlabel('Actual Precinct % Dem')
    plt.ylabel('Precinct % Dem predicted by \n'+ estimate_name)
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')


def partisan_error_fig(df,ground_truth_col_R, ground_truth_col_D, est_R, est_D, estimate_name,votes_lb, fig_name):
    fig, ax = plt.subplots()
    df['diff_pct'] =  (df[est_D]/(df[est_D]+df[est_R]) - df[ground_truth_col_D]/(df[ground_truth_col_D]+df[ground_truth_col_R]))
    plt.hist(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'], bins = [i/200 -1 for i in range(401)], color = 'tab:purple')
    plt.xlabel('Difference ('+estimate_name+' - ground truth)\n mean: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].mean(),3))+', sd: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].std(),3))+'\n filtered mean: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)&((df[ground_truth_col_R]+df[ground_truth_col_D])>votes_lb)]['diff_pct'].mean(),3))+', filtered sd: '+str(round(df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)&((df[ground_truth_col_R]+df[ground_truth_col_D])>votes_lb)]['diff_pct'].std(),3)))
    plt.ylabel('Frequency')
    plt.axvline(x = df[(df['diff_pct']< math.inf)&(df['diff_pct']> -1*math.inf)]['diff_pct'].mean(), color = 'k', lw = 2,alpha = .8, zorder = 2)
    plt.xlim(-.1,.1)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][(results_dfs[year]['race_description'] == elec)&(~results_dfs[year]['CTY'].isin([55,72]))]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         prec_partisan_df = elec_df[elec_df['cand_party'].isin(['DEM','REP'])].pivot_table(values = 'cand_tot_votes', columns = 'cand_party', index=['CTY','precinct'],aggfunc=np.sum).reset_index()
#         for method in ['elecday','cty_vote_method','combined_minus_elecday','scaled_minus_elecday','cty_vote_party','cty_vote_party_method']:
#             prec_partisan_df = prec_partisan_df.merge(elec_df[elec_df['cand_party'] == 'DEM'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_DEM'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
#             prec_partisan_df = prec_partisan_df.merge(elec_df[elec_df['cand_party'] == 'REP'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_REP'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
#         for cand in elec_df['cand_name'].unique():
#             cand_df = elec_df[elec_df['cand_name'] == cand]
#             assert(len(cand_df['cand_party'].unique()) == 1)
#             choice = list(cand_df['cand_party'].unique())[0]
#             if pd.isnull(choice):
#                 choice = cand.split(' ')[-1]
#             for vote_type in ['absmail', 'early', 'elecday']:
#                 cand_df['cand_'+vote_type+'_cty_votes'] = cand_df.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
#             for vote_type in ['absmail', 'early']:
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'elecday_votes_cty_pct',.95, 'Election Day Vote Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_elec_day_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'elecday_votes_cty_pct', 10, 'Elecday','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_elec_day_error.png')
#                 # error_map(cand_df,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'elecday_votes_cty_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_elec_day_error_map.png')
#                 # ### MAPS ###
#                 vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df['x']=cand_df['cand_'+vote_type+'_cty_votes']*cand_df['elecday_votes_cty_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df[['CTY','precinct','x']], how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
#                     prec_partisan_df['elecday_'+choice] = prec_partisan_df['elecday_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #ELECTION HISTORY BY METHOD
#                 elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                 elec_prec_hist_by_method = elec_prec_hist[elec_prec_hist['method_group']==vote_type_dict[vote_type]].groupby(['CTY','Precinct','method_group']).sum().reset_index()
#                 elec_prec_hist_by_method['cty_votes'] = elec_prec_hist_by_method.groupby('CTY')['votes'].transform('sum')
#                 elec_prec_hist_by_method['cty_vote_method_pct'] = elec_prec_hist_by_method['votes']/elec_prec_hist_by_method['cty_votes']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_by_method[['Precinct','cty_vote_method_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_method_pct',.95, 'Election History Method Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_method_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_method_pct', 10, 'History Method','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_method_error.png')
#                 # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_method_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_method_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_vote_method_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['cty_vote_method_'+choice] = prec_partisan_df['cty_vote_method_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #ELECTION HISTORY COMBINED MINUS ELEC-DAY
#                 elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                 elec_prec_hist_combined = elec_prec_hist.groupby(['CTY','Precinct']).sum().reset_index()
#                 elec_prec_hist_combined = elec_prec_hist_combined.merge(elec_df[['precinct','cand_elecday_votes']].groupby(['precinct']).sum().reset_index(), how = 'left', left_on='Precinct', right_on = 'precinct')
#                 elec_prec_hist_combined['combined_minus_elecday'] = elec_prec_hist_combined['votes']-elec_prec_hist_combined['cand_elecday_votes']
#                 elec_prec_hist_combined = elec_prec_hist_combined[(~elec_prec_hist_combined['combined_minus_elecday'].isna())&(elec_prec_hist_combined['combined_minus_elecday']>=0)]
#                 elec_prec_hist_combined['cty_votes'] = elec_prec_hist_combined.groupby('CTY')['combined_minus_elecday'].transform('sum')
#                 elec_prec_hist_combined['cty_combined_minus_elecday_pct'] = elec_prec_hist_combined['combined_minus_elecday']/elec_prec_hist_combined['cty_votes']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_combined[['Precinct','cty_combined_minus_elecday_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_combined_minus_elecday_pct',.95, 'Election History Combined Minus ElecDay','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_combined_minus_elecday_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_combined_minus_elecday_pct',10,  'History Combined Minus ElecDay','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_combined_minus_elecday_error.png')
#                 # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_combined_minus_elecday_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_combined_minus_elecday_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_combined_minus_elecday_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['combined_minus_elecday_'+choice] = prec_partisan_df['combined_minus_elecday_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #ADJUSTED ELECTION HISTORY COMBINED MINUS ELEC-DAY
#                 elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                 elec_prec_hist_combined = elec_prec_hist.groupby(['CTY','Precinct']).sum().reset_index()
#                 elec_prec_hist_combined = elec_prec_hist_combined.merge(elec_df[['precinct','cand_elecday_votes','cand_tot_votes']].groupby(['precinct']).sum().reset_index(), how = 'left', left_on='Precinct', right_on = 'precinct')
#                 elec_prec_hist_combined['returns_county_vote_sum'] = elec_prec_hist_combined.groupby('CTY')['cand_tot_votes'].transform('sum')
#                 elec_prec_hist_combined['history_county_vote_sum'] = elec_prec_hist_combined.groupby('CTY')['votes'].transform('sum')
#                 elec_prec_hist_combined['scaled_votes'] = elec_prec_hist_combined['votes']*elec_prec_hist_combined['returns_county_vote_sum']/elec_prec_hist_combined['history_county_vote_sum']
#                 elec_prec_hist_combined['scaled_minus_elecday'] = elec_prec_hist_combined['scaled_votes']-elec_prec_hist_combined['cand_elecday_votes']
#                 elec_prec_hist_combined = elec_prec_hist_combined[(~elec_prec_hist_combined['scaled_minus_elecday'].isna())&(elec_prec_hist_combined['scaled_minus_elecday']>=0)]
#                 elec_prec_hist_combined['cty_votes'] = elec_prec_hist_combined.groupby('CTY')['scaled_minus_elecday'].transform('sum')
#                 elec_prec_hist_combined['cty_scaled_minus_elecday_pct'] = elec_prec_hist_combined['scaled_minus_elecday']/elec_prec_hist_combined['cty_votes']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_combined[['Precinct','cty_scaled_minus_elecday_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_scaled_minus_elecday_pct',.95, 'Election History Scaled Minus ElecDay','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_scaled_minus_elecday_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_scaled_minus_elecday_pct', 10, 'History Scaled Minus ElecDay','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_scaled_minus_elecday_error.png')
#                 # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_scaled_minus_elecday_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_scaled_minus_elecday_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_scaled_minus_elecday_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['scaled_minus_elecday_'+choice] = prec_partisan_df['scaled_minus_elecday_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #ELECTION HISTORY BY PARTY
#                 if choice in elec_prec_hist['PolitalAff'].values:
#                     elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                     elec_prec_hist_by_party = elec_prec_hist[elec_prec_hist['PolitalAff']==choice].groupby(['CTY','Precinct','PolitalAff']).sum().reset_index()
#                     elec_prec_hist_by_party['cty_votes'] = elec_prec_hist_by_party.groupby('CTY')['votes'].transform('sum')
#                     elec_prec_hist_by_party['cty_vote_party_pct'] = elec_prec_hist_by_party['votes']/elec_prec_hist_by_party['cty_votes']
#                     cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_by_party[['Precinct','cty_vote_party_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                     # ### SCATTER ###
#                     # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_pct',.95, 'Election History Party Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_scatter.png')
#                     # ### ERROR ###
#                     # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_pct', 10, 'History Party','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_error.png')
#                     # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_error_map.png')
#                     ### PARTISAN ###
#                     if choice in ['DEM','REP']:
#                         cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_vote_party_pct']
#                         prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                         prec_partisan_df['cty_vote_party_'+choice] = prec_partisan_df['cty_vote_party_'+choice]+prec_partisan_df['x'].fillna(0)
#                         prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                     #ELECTION HISTORY BY PARTY AND METHOD
#                     elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                     elec_prec_hist_by_party_method = elec_prec_hist[(elec_prec_hist['PolitalAff']==choice)&(elec_prec_hist['method_group']==vote_type_dict[vote_type])].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                     elec_prec_hist_by_party_method['cty_votes'] = elec_prec_hist_by_party_method.groupby('CTY')['votes'].transform('sum')
#                     elec_prec_hist_by_party_method['cty_vote_party_method_pct'] = elec_prec_hist_by_party_method['votes']/elec_prec_hist_by_party_method['cty_votes']
#                     cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_by_party_method[['Precinct','cty_vote_party_method_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                     # ### SCATTER ###
#                     # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_method_pct',.95, 'Election History Party and Method Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_method_scatter.png')
#                     # ### ERROR ###
#                     # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_method_pct', 10, 'History Party and Method','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_method_error.png')
#                     # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_method_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_method_error_map.png')
#                     # error_correlation(cand_df_plot, ok_mggg, 'precinct', 'PRECODE','density',choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_party_method_pct', 10, 'History Party and Method','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_party_method_density_error_correlation.png')
#                     ### PARTISAN ###
#                     if choice in ['DEM','REP']:
#                         cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_vote_party_method_pct']
#                         prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                         prec_partisan_df['cty_vote_party_method_'+choice] = prec_partisan_df['cty_vote_party_method_'+choice]+prec_partisan_df['x'].fillna(0)
#                         prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#         for method in ['elecday','cty_vote_method','combined_minus_elecday','scaled_minus_elecday','cty_vote_party','cty_vote_party_method']:
#             partisan_scatter(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,'./figs/partisan/'+str(year)+'_'+elec_dict_name[elec]+'_'+ method+'_scatter.png')
#             partisan_error_fig(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,10, './figs/partisan/'+str(year)+'_'+elec_dict_name[elec]+'_'+ method+'_error.png')

# vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
# #By VAP and POC-VAP and TOTAL VOTERS
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][(results_dfs[year]['race_description'] == elec)&(~results_dfs[year]['CTY'].isin([55,72]))]
#         if elec == 'FOR US REPRESENTATIVE':
#             elec_df['cand_name'] = elec_df['cand_party']
#         prec_partisan_df = elec_df[elec_df['cand_party'].isin(['DEM','REP'])].pivot_table(values = 'cand_tot_votes', columns = 'cand_party', index=['CTY','precinct'],aggfunc=np.sum).reset_index()
#         for method in ['cty_vote','cty_VAP','w_and_pocvap_dist','w_and_pocvap_pct_dist','cty_AREA']:
#             prec_partisan_df = prec_partisan_df.merge(elec_df[elec_df['cand_party'] == 'DEM'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_DEM'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
#             prec_partisan_df = prec_partisan_df.merge(elec_df[elec_df['cand_party'] == 'REP'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_REP'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
#         for cand in elec_df['cand_name'].unique():
#             cand_df = elec_df[elec_df['cand_name'] == cand]
#             assert(len(cand_df['cand_party'].unique()) == 1)
#             choice = list(cand_df['cand_party'].unique())[0]
#             if pd.isnull(choice):
#                 choice = cand.split(' ')[-1]
#             for vote_type in ['absmail', 'early', 'elecday']:
#                 cand_df['cand_'+vote_type+'_cty_votes'] = cand_df.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
#             for vote_type in ['absmail', 'early']:
#                 vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
#                 #ELECTION HISTORY BY TOTAL VOTERS
#                 elec_prec_hist = prec_hist[prec_hist['ElectionDate']=='11/'+dates[year][-2:]+'/'+str(year)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
#                 elec_prec_hist_by_method = elec_prec_hist.groupby(['CTY','Precinct']).sum().reset_index()
#                 elec_prec_hist_by_method['cty_votes'] = elec_prec_hist_by_method.groupby('CTY')['votes'].transform('sum')
#                 elec_prec_hist_by_method['cty_vote_pct'] = elec_prec_hist_by_method['votes']/elec_prec_hist_by_method['cty_votes']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(elec_prec_hist_by_method[['Precinct','cty_vote_pct']], how = 'left', left_on = 'precinct', right_on ='Precinct')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_pct',.95, 'Election History Voter Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_tot_votes_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_pct',10,  'History Total Voters','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_tot_votes_error.png')
#                 # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_vote_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_history_tot_votes_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_vote_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['cty_vote_'+choice] = prec_partisan_df['cty_vote_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #BY VAP
#                 ok_vap = ok_mggg[['COUNTY','PRECODE','VAP','WVAP']]
#                 ok_vap['cty_VAP'] = ok_vap.groupby('COUNTY')['VAP'].transform('sum')
#                 ok_vap['cty_VAP_pct'] = ok_vap['VAP']/ok_vap['cty_VAP']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(ok_vap[['PRECODE','cty_VAP_pct']], how = 'left', left_on = 'precinct', right_on ='PRECODE')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_VAP_pct',.95, 'VAP Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_VAP_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_VAP_pct',10,  'VAP','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_VAP_error.png')
#                 # error_map(cand_df_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_VAP_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_VAP_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_VAP_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['cty_VAP_'+choice] = prec_partisan_df['cty_VAP_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #BY POC-VAP
#                 ok_vap = ok_mggg[['COUNTY','PRECODE','VAP','WVAP']]
#                 ok_vap['POCVAP'] = ok_vap['VAP'] - ok_vap['WVAP']
#                 ok_vap['cty_VAP'] = ok_vap.groupby('COUNTY')['VAP'].transform('sum')
#                 ok_vap['cty_WVAP'] = ok_vap.groupby('COUNTY')['WVAP'].transform('sum')
#                 ok_vap['cty_POCVAP'] = ok_vap['cty_VAP'] - ok_vap['cty_WVAP']
#                 ok_vap['cty_WVAP_pct'] = ok_vap['WVAP']/ok_vap['cty_WVAP']
#                 ok_vap['cty_POCVAP_pct'] = ok_vap['POCVAP']/ok_vap['cty_POCVAP']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(ok_vap[['PRECODE','cty_WVAP_pct','cty_POCVAP_pct']], how = 'left', left_on = 'precinct', right_on ='PRECODE')
#                 if choice == 'DEM':
#                     cand_df_plot['w_and_pocvap_dist'] = cand_df_plot['cty_POCVAP_pct']
#                 else:
#                     cand_df_plot['w_and_pocvap_dist'] = cand_df_plot['cty_WVAP_pct']
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_dist',.95, 'W/POC VAP Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_dist',10,  'W/POC VAP','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_error.png')
#                 # error_map(cand_df_plot,ok,'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_dist', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['w_and_pocvap_dist']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['w_and_pocvap_dist_'+choice] = prec_partisan_df['w_and_pocvap_dist_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #BY POC-VAP pct
#                 ok_vap = ok_mggg[['COUNTY','PRECODE','VAP','WVAP']]
#                 ok_vap['WVAP_pct'] = ok_vap['WVAP']/ok_vap['VAP']
#                 ok_vap['POCVAP_pct'] = 1-ok_vap['WVAP_pct']
#                 ok_vap['cty_WVAP_pct'] = ok_vap.groupby('COUNTY')['WVAP_pct'].transform('sum')
#                 ok_vap['cty_POCVAP_pct'] = ok_vap.groupby('COUNTY')['POCVAP_pct'].transform('sum')
#                 ok_vap['cty_WVAP_pct_pct'] = ok_vap['WVAP_pct']/ok_vap['cty_WVAP_pct']
#                 ok_vap['cty_POCVAP_pct_pct'] = ok_vap['POCVAP_pct']/ok_vap['cty_POCVAP_pct']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(ok_vap[['PRECODE','cty_WVAP_pct_pct','cty_POCVAP_pct_pct']], how = 'left', left_on = 'precinct', right_on ='PRECODE')
#                 if choice == 'DEM':
#                     cand_df_plot['w_and_pocvap_pct_dist'] = cand_df_plot['cty_POCVAP_pct_pct']
#                 else:
#                     cand_df_plot['w_and_pocvap_pct_dist'] = cand_df_plot['cty_WVAP_pct_pct']
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_pct_dist',.95, 'W/POC VAP PCT Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_pct_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_pct_dist', 10, 'W/POC VAP PCT','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_pct_error.png')
#                 # error_map(cand_df_plot,ok,'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'w_and_pocvap_pct_dist', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_W_POC_VAP_pct_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['w_and_pocvap_pct_dist']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['w_and_pocvap_pct_dist_'+choice] = prec_partisan_df['w_and_pocvap_pct_dist_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#                 #BY AREA
#                 ok_area = ok_mggg[['COUNTY','PRECODE','AREA']]
#                 ok_area['cty_AREA'] = ok_area.groupby('COUNTY')['AREA'].transform('sum')
#                 ok_area['cty_AREA_pct'] = ok_area['AREA']/ok_area['cty_AREA']
#                 cand_df_plot = cand_df[['precinct','cand_'+vote_type+'_votes','cand_'+vote_type+'_cty_votes']].merge(ok_area[['PRECODE','cty_AREA_pct']], how = 'left', left_on = 'precinct', right_on ='PRECODE')
#                 # ### SCATTER ###
#                 # scatter_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_AREA_pct',.95, 'AREA Distribution','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_AREA_scatter.png')
#                 # ### ERROR ###
#                 # error_fig(cand_df_plot,choice, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_AREA_pct',10,  'AREA','./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_AREA_error.png')
#                 # error_map(cand_df_plot,ok,'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_AREA_pct', 10,'./figs/compare/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_v_AREA_error_map.png')
#                 ### PARTISAN ###
#                 if choice in ['DEM','REP']:
#                     cand_df_plot['x']=cand_df_plot['cand_'+vote_type+'_cty_votes']*cand_df_plot['cty_AREA_pct']
#                     prec_partisan_df = prec_partisan_df.merge(cand_df_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
#                     prec_partisan_df['cty_AREA_'+choice] = prec_partisan_df['cty_AREA_'+choice]+prec_partisan_df['x'].fillna(0)
#                     prec_partisan_df = prec_partisan_df.drop('x',axis=1)
#         for method in ['cty_vote','cty_VAP','w_and_pocvap_dist','w_and_pocvap_pct_dist','cty_AREA']:
#             partisan_scatter(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,'./figs/partisan/'+str(year)+'_'+elec_dict_name[elec]+'_'+ method+'_scatter.png')
#             partisan_error_fig(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,10, './figs/partisan/'+str(year)+'_'+elec_dict_name[elec]+'_'+ method+'_error.png')




# def scatter_plot(df1,col1,joincol1,df2,col2,joincol2,color, xlabel, ylabel,title,fig_name, symmetric = False, regression_line = False):
#     df1_plot = df1[[col1,joincol1]].rename(columns = {col1:'X'})
#     df2_plot = df2[[col2,joincol2]].rename(columns = {col2:'Y'})
#     df1_plot = df1_plot.merge(df2_plot, how = 'left', left_on = joincol1, right_on = joincol2)
#     df1_plot = df1_plot[(~df1_plot['Y'].isna())&(~df1_plot['X'].isna())]
#     plt.figure()
#     plt.scatter(df1_plot['X'],df1_plot['Y'], alpha = .2, color =color)
#     max_x_val = df1_plot['X'].max()
#     min_x_val = min(0,df1_plot['X'].min())
#     max_y_val = df1_plot['Y'].max()
#     min_y_val = min(0,df1_plot['Y'].min())
#     if symmetric:
#         max_val = max(max_x_vals, max_y_val)
#         min_val = min(min_x_vals, min_y_val)
#         plt.plot([min_val*2,max_val*2],[min_val*2,max_val*2], color = 'k',zorder=2)
#         plt.xlim(min_val-.05*(max_val-min_val),max_val*1.05)
#         plt.ylim(min_val-.05*(max_val-min_val),max_val*1.05)
#     else:
#         plt.xlim(min_x_val-.05*(max_x_val-min_x_val),max_x_val*1.05)
#         plt.ylim(min_y_val-.05*(max_y_val-min_y_val),max_y_val*1.05)
#     if regression_line:
#         m, b = np.polyfit(np.array(df1_plot['X']),np.array(df1_plot['Y']), 1)
#         plt.plot(np.array(df1_plot['X']), m*np.array(df1_plot['X']) + b, color = 'gray')
#         title = title + '\n '+str(round(m,4))+'x + '+str(round(b,4))
#     plt.xlabel(xlabel)
#     plt.ylabel(ylabel)
#     plt.title(title)
#     plt.tight_layout()
#     plt.savefig(fig_name)
#     plt.close('all')


# def map_plot(df,col1, joincol1, gdf, joincol2, fig_name, cmap = 'viridis'):
#     df_plot = df[[col1,joincol1]]
#     ok_plot = gdf.merge(df_plot, how = 'left', left_on = joincol2, right_on = joincol1)
#     fig, ax = plt.subplots()
#     ok_plot.plot(column = col1,cmap = cmap,ax=ax,missing_kwds= dict(color = "gray"), legend = True)
#     ok_cty.geometry.boundary.plot(color=None,edgecolor='k',linewidth = 1,ax=ax)
#     ax.set_axis_off()
#     plt.tight_layout()
#     plt.savefig(fig_name, dpi = 300)
#     plt.close('all')


# #compare 2016 to 2020
# for elec16,elec20 in [('FOR PRESIDENT AND VICE PRESIDENT','FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT'),('FOR UNITED STATES SENATOR','FOR UNITED STATES SENATOR'),('FOR US REPRESENTATIVE','FOR US REPRESENTATIVE')]:
#     elec_16 = results_dfs[2016][(results_dfs[2016]['race_description'] == elec16)&(~results_dfs[2016]['CTY'].isin([55,72]))]
#     elec_20 = results_dfs[2020][(results_dfs[2020]['race_description'] == elec20)&(~results_dfs[2020]['CTY'].isin([55,72]))]
#     for party in ['REP','DEM']:
#         party_16 = elec_16[elec_16['cand_party'] == party]
#         party_20 = elec_20[elec_20['cand_party'] == party]
#         for vote_type in ['absmail', 'early', 'elecday','tot']:
#             scatter_plot(party_16,'cand_'+vote_type+'_votes','precinct', party_20,'cand_'+vote_type+'_votes','precinct',color_dict[party],'2016 '+vote_type + ' prec votes' ,'2020 '+vote_type + ' prec votes','2016 v 2020 ' +vote_type+ ' '+party + ' prec votes','./figs/compare_years/'+elec_dict_name[elec16]+'vote_diff_16_20_'+party+'_'+vote_type+'.png')
#             party_16[vote_type+'_prec_pct'] = party_16['cand_'+vote_type+'_votes']/party_16['cand_tot_votes']
#             party_20[vote_type+'_prec_pct'] = party_20['cand_'+vote_type+'_votes']/party_20['cand_tot_votes']
#             scatter_plot(party_16,vote_type+'_prec_pct','precinct',party_20,vote_type+'_prec_pct','precinct',color_dict[party],'2016 '+vote_type + ' prec pct' ,'2020 '+vote_type + ' prec pct','2016 v 2020 ' +vote_type+ ' '+party + ' prec pct','./figs/compare_years/'+elec_dict_name[elec16]+'vote_pct_diff_16_20_'+party+'_'+vote_type+'.png')
#     all_16 = elec_16[['CTY','precinct','cand_absmail_votes', 'cand_early_votes','cand_elecday_votes', 'cand_tot_votes']].groupby(['CTY','precinct']).sum().reset_index()
#     all_20 = elec_20[['CTY','precinct','cand_absmail_votes', 'cand_early_votes','cand_elecday_votes', 'cand_tot_votes']].groupby(['CTY','precinct']).sum().reset_index()
#     for vote_type in ['absmail', 'early', 'elecday','tot']:
#         scatter_plot(all_16,'cand_'+vote_type+'_votes','precinct', all_20,'cand_'+vote_type+'_votes','precinct',color_dict['all'],'2016 '+vote_type + ' votes' ,'2020 '+vote_type + ' votes','2016 v 2020 all ' +vote_type+ ' votes','./figs/compare_years/'+elec_dict_name[elec16]+'vote_diff_16_20_all_'+vote_type+'.png')
#         all_16[vote_type+'_prec_pct'] = all_16['cand_'+vote_type+'_votes']/all_16['cand_tot_votes']
#         all_20[vote_type+'_prec_pct'] = all_20['cand_'+vote_type+'_votes']/all_20['cand_tot_votes']
#         scatter_plot(all_16,vote_type+'_prec_pct','precinct',all_20,vote_type+'_prec_pct','precinct',color_dict['all'],'2016 '+vote_type + ' prec pct' ,'2020 '+vote_type + ' prec pct','2016 v 2020 all ' +vote_type+ ' prec pct','./figs/compare_years/'+elec_dict_name[elec16]+'vote_pct_diff_16_20_all_'+vote_type+'.png')

vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
#use 2016 to estimate 2020
for elec16,elec20 in [('FOR PRESIDENT AND VICE PRESIDENT','FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT'),('FOR UNITED STATES SENATOR','FOR UNITED STATES SENATOR'),('FOR US REPRESENTATIVE','FOR US REPRESENTATIVE')]:
    elec_16 = results_dfs[2016][(results_dfs[2016]['race_description'] == elec16)&(~results_dfs[2016]['CTY'].isin([55,72]))]
    elec_20 = results_dfs[2020][(results_dfs[2020]['race_description'] == elec20)&(~results_dfs[2020]['CTY'].isin([55,72]))]
    prec_partisan_df = elec_20[elec_20['cand_party'].isin(['DEM','REP'])].pivot_table(values = 'cand_tot_votes', columns = 'cand_party', index=['CTY','precinct'],aggfunc=np.sum).reset_index()
    for method in ['cty_2016_adjusted_party_method']:
        prec_partisan_df = prec_partisan_df.merge(elec_20[elec_20['cand_party'] == 'DEM'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_DEM'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
        prec_partisan_df = prec_partisan_df.merge(elec_20[elec_20['cand_party'] == 'REP'][['CTY','precinct','cand_elecday_votes']].rename(columns = {'cand_elecday_votes':method+'_REP'}), how = 'left', left_on = ['CTY','precinct'], right_on = ['CTY','precinct'])
    for party in ['REP','DEM']:
        party_16 = elec_16[elec_16['cand_party'] == party]
        party_20 = elec_20[elec_20['cand_party'] == party]
        for vote_type in ['absmail', 'early']:
            #2016_adjusted simple subtraction
            party_16['cand_'+vote_type+'_cty_votes16'] = party_16.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
            party_20['cand_'+vote_type+'_cty_votes'] = party_20.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
            elec_prec_hist16 = prec_hist[prec_hist['ElectionDate']=='11/'+dates[2016][-2:]+'/'+str(2016)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            elec_prec_hist20 = prec_hist[prec_hist['ElectionDate']=='11/'+dates[2020][-2:]+'/'+str(2020)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            elec_prec_hist_by_party_method16 = elec_prec_hist16[(elec_prec_hist16['PolitalAff']==party)&(elec_prec_hist16['method_group']==vote_type_dict[vote_type])].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            elec_prec_hist_by_party_method20 = elec_prec_hist20[(elec_prec_hist20['PolitalAff']==party)&(elec_prec_hist20['method_group']==vote_type_dict[vote_type])].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            elec_prec_hist_by_party_method20 = elec_prec_hist_by_party_method20.merge(elec_prec_hist_by_party_method16[['Precinct','votes']].rename(columns = {'votes':'votes16'}), how = 'left', left_on = 'Precinct', right_on = 'Precinct').fillna(0)
            elec_prec_hist_by_party_method20['votes_diff'] = elec_prec_hist_by_party_method20.apply(lambda x: max(0,x['votes']-x['votes16']),axis=1)
            elec_prec_hist_by_party_method20['cty_votes16'] = elec_prec_hist_by_party_method20.groupby('CTY')['votes16'].transform('sum')
            elec_prec_hist_by_party_method20['cty_votes_diff'] = elec_prec_hist_by_party_method20.groupby('CTY')['votes_diff'].transform('sum')
            elec_prec_hist_by_party_method20['cty_vote16_party_method_pct'] = elec_prec_hist_by_party_method20['votes16']/elec_prec_hist_by_party_method20['cty_votes16']
            elec_prec_hist_by_party_method20['cty_vote_diff_party_method_pct'] = elec_prec_hist_by_party_method20['votes_diff']/elec_prec_hist_by_party_method20['cty_votes_diff']
            party_20_plot = party_20.merge(party_16[['precinct','cand_'+vote_type+'_cty_votes16']], how = 'left', left_on = 'precinct', right_on = 'precinct')
            party_20_plot = party_20_plot.merge(elec_prec_hist_by_party_method20[['Precinct','cty_vote16_party_method_pct','cty_vote_diff_party_method_pct']], how = 'left', left_on = 'precinct', right_on = 'Precinct')
            party_20_plot['cty_2016_adjusted_party_method_pct'] = party_20_plot['cty_vote16_party_method_pct']*(party_20_plot['cand_'+vote_type+'_cty_votes16']/party_20_plot['cand_'+vote_type+'_cty_votes'])+party_20_plot['cty_vote_diff_party_method_pct']*(1-party_20_plot['cand_'+vote_type+'_cty_votes16']/party_20_plot['cand_'+vote_type+'_cty_votes'])
            # ### SCATTER ###
            # scatter_fig(party_20_plot,party, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct',.95, '2016-adjusted Election History Party and Method Distribution','./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_scatter.png')
            # ### ERROR ###
            # error_fig(party_20_plot,party, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct', 10, '2016-adjusted  History Party and Method','./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_error.png')
            # error_map(party_20_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct', 10,'./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_error_map.png')
            ### PARTISAN ###
            party_20_plot['x']=party_20_plot['cand_'+vote_type+'_cty_votes']*party_20_plot['cty_2016_adjusted_party_method_pct']
            prec_partisan_df = prec_partisan_df.merge(party_20_plot[['precinct','x']], how = 'left', left_on = ['precinct'], right_on = ['precinct'])
            prec_partisan_df['cty_2016_adjusted_party_method_'+party] = prec_partisan_df['cty_2016_adjusted_party_method_'+party]+prec_partisan_df['x'].fillna(0)
            prec_partisan_df = prec_partisan_df.drop('x',axis=1)
            # #2016_adjusted accounting for voter drop off
            # party_16['cand_'+vote_type+'_cty_votes16'] = party_16.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
            # party_20['cand_'+vote_type+'_cty_votes'] = party_20.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
            # elec_prec_hist16 = prec_hist[prec_hist['ElectionDate']=='11/'+dates[2016][-2:]+'/'+str(2016)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            # elec_prec_hist20 = prec_hist[prec_hist['ElectionDate']=='11/'+dates[2020][-2:]+'/'+str(2020)].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            # elec_prec_hist_by_party_method16 = elec_prec_hist16[(elec_prec_hist16['PolitalAff']==party)&(elec_prec_hist16['method_group']==vote_type_dict[vote_type])].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            # elec_prec_hist_by_party_method20 = elec_prec_hist20[(elec_prec_hist20['PolitalAff']==party)&(elec_prec_hist20['method_group']==vote_type_dict[vote_type])].groupby(['CTY','Precinct','method_group','PolitalAff']).sum().reset_index()
            # elec_prec_hist_by_party_method20 = elec_prec_hist_by_party_method20.merge(elec_prec_hist_by_party_method16[['Precinct','votes']].rename(columns = {'votes':'votes16'}), how = 'left', left_on = 'Precinct', right_on = 'Precinct').fillna(0)
            # elec_prec_hist_by_party_method20['votes_diff'] = elec_prec_hist_by_party_method20.apply(lambda x: max(0,x['votes']-x['votes16']),axis=1)
            # elec_prec_hist_by_party_method20['cty_votes16'] = elec_prec_hist_by_party_method20.groupby('CTY')['votes16'].transform('sum')
            # elec_prec_hist_by_party_method20['cty_votes_diff'] = elec_prec_hist_by_party_method20.groupby('CTY')['votes_diff'].transform('sum')
            # elec_prec_hist_by_party_method20['cty_vote16_party_method_pct'] = elec_prec_hist_by_party_method20['votes16']/elec_prec_hist_by_party_method20['cty_votes16']
            # elec_prec_hist_by_party_method20['cty_vote_diff_party_method_pct'] = elec_prec_hist_by_party_method20['votes_diff']/elec_prec_hist_by_party_method20['cty_votes_diff']
            # party_20_plot = party_20.merge(party_16[['precinct','cand_'+vote_type+'_cty_votes16']], how = 'left', left_on = 'precinct', right_on = 'precinct')
            # party_20_plot = party_20_plot.merge(elec_prec_hist_by_party_method20[['Precinct','cty_vote16_party_method_pct','cty_vote_diff_party_method_pct']], how = 'left', left_on = 'precinct', right_on = 'Precinct')
            # party_20_plot['cty_2016_adjusted_party_method_pct'] = party_20_plot['cty_vote16_party_method_pct']*(party_20_plot['cand_'+vote_type+'_cty_votes16']/party_20_plot['cand_'+vote_type+'_cty_votes'])+party_20_plot['cty_vote_diff_party_method_pct']*(1-party_20_plot['cand_'+vote_type+'_cty_votes16']/party_20_plot['cand_'+vote_type+'_cty_votes'])
            # ### SCATTER ###
            # scatter_fig(party_20_plot,party, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct',.95, '2016-adjusted Election History Party and Method Distribution','./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_scatter.png')
            # ### ERROR ###
            # error_fig(party_20_plot,party, vote_type, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct', 10, '2016-adjusted  History Party and Method','./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_error.png')
            # error_map(party_20_plot,ok, 'cand_'+vote_type+'_votes', 'cand_'+vote_type+'_cty_votes', 'cty_2016_adjusted_party_method_pct', 10,'./figs/compare/'+str(2020)+'_'+elec_dict_name[elec20]+'_'+party+'_'+vote_type+'_v_16adj_history_party_method_error_map.png')
    for method in ['cty_2016_adjusted_party_method']:
        partisan_scatter(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,'./figs/partisan/'+str(year)+'_'+elec_dict_name[elec20]+'_'+ method+'_scatter.png')
        partisan_error_fig(prec_partisan_df,'REP', 'DEM', method+'_REP',  method+'_DEM', method,10, './figs/partisan/'+str(year)+'_'+elec_dict_name[elec20]+'_'+ method+'_error.png')





# # density vote type correlation
# for year in dates.keys():
#     for elec in elec_dict[year]:
#         elec_df = results_dfs[year][(results_dfs[year]['race_description'] == elec)&(~results_dfs[year]['CTY'].isin([55,72]))]
#         for choice in ['REP','DEM']:
#             choice_df = elec_df[elec_df['cand_party'] == choice]
#             for vote_type in ['absmail', 'early', 'elecday']:
#                 choice_df['cand_'+vote_type+'_cty_votes'] = choice_df.groupby('CTY')['cand_'+vote_type+'_votes'].transform('sum')
#             for vote_type in ['absmail', 'early','elecday']:
#                 vote_type_dict = {'absmail':'Absentee', 'early':'Early', 'elecday':'In Person'}
#                 choice_df['cand_'+vote_type+'_prec_pct'] = choice_df['cand_'+vote_type+'_votes']/choice_df['cand_tot_votes']
#                 scatter_plot(ok_mggg,'log_density','PRECODE',choice_df,'cand_'+vote_type+'_prec_pct','precinct',color_dict[choice], 'log Density', 'Percent Precinct '+vote_type_dict[vote_type]+' Votes','Density v '+vote_type_dict[vote_type]+ ' Votes','./figs/density_scatter/'+str(year)+'_'+elec_dict_name[elec]+'_'+choice+'_'+vote_type+'_density_scatter.png', regression_line = True)



# map_plot(ok_mggg,'log_density', 'PRECODE', ok_mggg.drop('log_density',axis=1), 'PRECODE', './figs/prec_log_density.png')

# # ok_data1 = pd.read_csv('./nhgis0021_csv/nhgis0021_ds176_20105_2010_state.csv')
# # ok_data2 = pd.read_csv('./nhgis0021_csv/nhgis0021_ds172_2010_state.csv')
# # ok_data3 = pd.read_csv('./nhgis0022_csv/nhgis0022_ds171_2010_state.csv')
# # ok_data4 = pd.read_csv('./nhgis0022_csv/nhgis0022_ds172_2010_state.csv')




# # IP = Voted in person at polling place
# # AI = Voted absentee in person
# # AB = Absentee
# # PI = Physically Incapacitated
# # CI = Absentee - Care of Physically Incapacitated
# # EI = Absentee - Emergency Incapacitated
# # MI = Absentee - Military
# # OV = Absentee - Overseas
# # NH = Absentee - Nursing Home Voter


# # TOTPOP                                                3751351
# # NH_WHITE                                              2575381
# # NH_BLACK                                               272071
# # NH_AMIN                                                308733
# # NH_ASIAN                                                64154
# # NH_NHPI                                                  3977
# # NH_OTHER                                                 2954
# # NH_2MORE                                               192074
# # HISP                                                   332007

# # TOT           3751351
# # HPOP           332007
# # NH_WPOP       2575381
# # NH_BPOP        272071
# # NH_AMINPOP     308733