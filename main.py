# -*- coding: utf-8 -*-
import requests
import sys
from PIL import Image
import io
import os
import re

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

from time import gmtime, strftime
from aquarel import load_theme

theme = load_theme("solarized_light")
theme.set_color(figure_background_color='#fdf6e3', plot_background_color='#eee8d5')

try:
    E_ID = os.environ['E_ID']
    RPLY_ID = os.environ['RPLY_ID']
except:
    E_ID = 'x'
    RPLY_ID = 'y'

def sc2replaystats_df(game_dat):

    df = pd.DataFrame(game_dat)

    dat_keys = ['race','mmr','division','apm','team','winner']
    opp = []
    upa = []


    for index, row in df.iterrows():
        players = dict()
        for p, n in zip(row['players'],np.arange(len(df.loc[0,'players']))):
            player = dict()
            player['id'] = p['player']['battle_tag_name']
            for k in dat_keys:
                player[k] = p[k]

            if player['id'] == 'UpATree':
                upa.append(player)
            else:
                opp.append(player)

    u_df = pd.DataFrame(upa)
    o_df = pd.DataFrame(opp)

    u_df = u_df.join(o_df, lsuffix='_UpATree', rsuffix='_Opp')

    df = df.join(u_df)

    return df

def generate_streak_info(df, column='winner_UpATree'):
    data = df[column].to_frame()
    data['start_of_streak'] = data[column].ne(data[column].shift())
    data['streak_id'] = data.start_of_streak.cumsum()
    data['streak_counter'] = data.groupby('streak_id').cumcount() + 1
    shots_with_streaks = pd.concat([df, data['streak_counter']], axis=1)
    return shots_with_streaks

tk_res = requests.post('https://api.sc2replaystats.com/account/login', 
                       data = {'email_address':E_ID, 'password':RPLY_ID})
try:
    tk = tk_res.json()['token']
except:
    tk='x'
    with open("log.txt", "a") as f:
        f.write(f"Not Getting Token. Error {tk_res.status_code}\n")
        f.write(f"Not Getting Token. Error {E_ID}\n")

tk_header = {'Authorization': f'{tk}'}


# make initial request
res = requests.get('https://api.sc2replaystats.com/player/1384133/replays/62', headers=tk_header)
npages = 0

# determine the number of pages we are looking at
if res.status_code==200:
    npages = res.json()['total_items'] // res.json()['items_per_page'] 
    if res.json()['total_items'] % res.json()['items_per_page'] > 1: npages = npages + 1

# load the last page and put data into dataframe
p_res = requests.get('https://api.sc2replaystats.com/player/1384133/replays/62', 
                     headers=tk_header, params={'page': npages})
if p_res.status_code == 200:
    gm_df = sc2replaystats_df(p_res.json()['items']) 
    gm_df = gm_df.drop(columns='players') 
    game_df = pd.read_csv('UpATree.csv.gz')
    game_df = game_df.drop(columns='Unnamed: 0')
    game_df = pd.concat([game_df,gm_df], ignore_index=True)
    game_df = game_df.drop_duplicates(subset='replay_url')
    game_df.to_csv('UpATree.csv.gz',compression='gzip')


# load subathon data that was retrieved from sc2replaystats
# and read the game columns
sheet = 'UpATree.csv.gz'

game_df = pd.read_csv('UpATree.csv.gz')
game_df = game_df.drop_duplicates(subset='replay_url')
try:
    game_df['DateTime'] = pd.to_datetime(game_df['replay_date'].str[:19])
    game_df['DOY'] = game_df['DateTime'].apply(lambda x: x.dayofyear)
except:
    with open("log.txt", "a") as f:
        f.write(f"Exiting on DateTime\n")
    sys.exit()

game_df['dMMR'] = game_df['mmr_UpATree'].diff(periods=1)
game_df = generate_streak_info(game_df)

game_df['Win Streak'] = game_df['streak_counter']
game_df.loc[game_df['winner_UpATree']==0,'Win Streak']=-1

game_df['Loss Streak'] = game_df['streak_counter']
game_df.loc[game_df['winner_UpATree']==1,'Loss Streak']=-1


# drop outliers of mmr
q_low = game_df["mmr_UpATree"].quantile(0.05)
q_hi  = game_df["mmr_UpATree"].quantile(0.99)
mmr_p = (game_df["mmr_UpATree"] < q_hi) & (game_df["mmr_UpATree"] > q_low)

# create MMR plot and save it to assets
theme.apply()
game_df[mmr_p].plot(y='mmr_UpATree',
                    label="Sal's MMR", 
                    xlabel='Game', ylabel='MMR')
theme.apply_transforms()
plt.gcf().savefig('./docs/assets/MMR.png',bbox_inches='tight')

# Daily Stats
win_d = game_df.groupby('DOY')['winner_UpATree'].sum()
win_d.name='W'
loss_d = game_df[game_df['winner_UpATree']==0].groupby('DOY')['winner_UpATree'].count()
loss_d.name='L'

day_df = pd.concat([win_d,loss_d], axis=1)
day_df = day_df.reset_index()
theme.apply()
ax = day_df.plot.bar(x='DOY', y=['W','L'], stacked=True)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
theme.apply_transforms()
plt.gcf().savefig('./docs/assets/daily.png', bbox_inches='tight')

#gm hist plot
gm_hist = pd.concat([game_df.tail(10)['winner_UpATree'].reset_index(drop=True).rename('All'),
                     game_df[game_df['race_Opp'] == 'T'].tail(10)['winner_UpATree'].reset_index(drop=True).rename('Terran'),
                     game_df[game_df['race_Opp'] == 'Z'].tail(10)['winner_UpATree'].reset_index(drop=True).rename('Zerg'),
                     game_df[game_df['race_Opp'] == 'P'].tail(10)['winner_UpATree'].reset_index(drop=True).rename('Protoss')],
                    axis=1)

theme.apply()
fig, ax = plt.subplots(figsize = (6, 2)) 
heatmap = sns.heatmap(gm_hist.transpose(), xticklabels=np.arange(0,10)-10,
                      cmap=['#2aa198','#d33682'], vmin=-0.4, vmax=1.4, linewidth=.5, cbar=False)
heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0)
heatmap.set(xlabel='Last Played Game')
heatmap.set(ylabel='Vs')

w_patch = mpatches.Patch(color='#2aa198', label='Win')
l_patch = mpatches.Patch(color='#d33682', label='Loss')
ax.legend(handles=[w_patch,l_patch], fancybox=True)

fig.tight_layout()
theme.apply_transforms()
fig.savefig('./docs/assets/gm_hist.png', bbox_inches='tight')

# wrt per race as a function of time
tw = game_df[game_df['race_Opp'] == 'T'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].sum().rename('Terran Wins')
tg = game_df[game_df['race_Opp'] == 'T'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].count().rename('Terran Games')

pw = game_df[game_df['race_Opp'] == 'P'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].sum().rename('Protoss Wins')
pg = game_df[game_df['race_Opp'] == 'P'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].count().rename('Protoss Games')

zw = game_df[game_df['race_Opp'] == 'Z'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].sum().rename('Zerg Wins')
zg = game_df[game_df['race_Opp'] == 'Z'].groupby(pd.cut(game_df['game_length'],np.arange(0,31*60,60)))['winner_UpATree'].count().rename('Zerg Games')

gm_ln_wrt = pd.concat([tw,tg,pw,pg,zw,zg], axis=1).reset_index(drop=True)
gm_ln_wrt['Z wrt'] = gm_ln_wrt['Zerg Wins']/gm_ln_wrt['Zerg Games']
gm_ln_wrt['P wrt'] = gm_ln_wrt['Protoss Wins']/gm_ln_wrt['Protoss Games']
gm_ln_wrt['T wrt'] = gm_ln_wrt['Terran Wins']/gm_ln_wrt['Terran Games']

theme.apply()
gm_ln_wrt.rolling(3).mean().plot(y=['Z wrt','P wrt', 'T wrt'], 
                                 ylabel='Win Rate',xlabel='Game Duration', xlim=[0,30])
theme.apply_transforms()
plt.gcf().savefig('./docs/assets/r_wrt.png', bbox_inches='tight')

# create first table
t1 = pd.DataFrame([game_df.shape[0],
                   game_df.loc[(game_df['dMMR'] > 0) & (game_df['dMMR'] < 100),"dMMR"].sum(),
                   abs(game_df.loc[(game_df['dMMR'] < 0) & (game_df['dMMR'] > -100),"dMMR"].sum()),
                   game_df.loc[mmr_p,'mmr_UpATree'].max(),
                   game_df.loc[mmr_p,'mmr_UpATree'].min(),
                   game_df['Win Streak'].max(),
                   game_df['Loss Streak'].max(),
                   game_df['mmr_Opp'].max(),
                   game_df.loc[game_df['mmr_Opp']>0,'mmr_Opp'].min(),
                   ], 
                   columns=['Stats'],
                   index=['Matches Played','MMR Gained', 'MMR lost', 'Max MMR', 'Min MMR',
                          'Longest Win Streak', 'Longest Loss Streak', 'Highest MMR Beaten',
                          'Lowest MMR Thrown to'])
t1 = t1.astype('int')

# create nemesis table
nem = game_df[(game_df['dMMR']<0) & (game_df['dMMR']>-100)].groupby('id_Opp')['dMMR'].sum()
nem = nem.rename(index='ΔMMR').rename_axis('Opponent')
nem = nem.sort_values()[0:10].abs().to_frame()
nem = nem.astype('int')

# win rate table
r_wrt = pd.concat([game_df.groupby('race_Opp')['winner_UpATree'].sum().rename('Wins'),
                   game_df.groupby('race_Opp')['winner_UpATree'].count().rename('Total'),
                   game_df[(game_df['dMMR']>0) & (game_df['dMMR']<100) & (mmr_p)].groupby('race_Opp')['dMMR'].sum().rename('MMR Gained'),
                   game_df[(game_df['dMMR']<0) & (game_df['dMMR']>-100) & (mmr_p)].groupby('race_Opp')['dMMR'].sum().rename('MMR Lost')]
                   ,axis=1)

r_wrt['Losses'] = r_wrt['Total']-r_wrt['Wins']
r_wrt['Win Rate (%)'] = 100*r_wrt['Wins']/r_wrt['Total']

r_wrt = r_wrt[['Wins','Losses','Total','Win Rate (%)', 'MMR Gained', 'MMR Lost']]
r_wrt['MMR Lost'] = r_wrt['MMR Lost'].abs().to_frame() 

r_wrt = r_wrt.rename(index={'P':'Protoss', 'T':'Terran', 'Z':'Zerg'})
r_wrt.index.names = ['Race']

stat_tab = re.sub(' class="dataframe"', '', t1.reset_index(names='').to_html(border=0,index=False))
nem_tab = re.sub(' class="dataframe"', '', nem.reset_index().to_html(border=0,index=False))

# create main page
index = f'''---
layout: home
---

<h1><img class="circular_image" src="https://static-cdn.jtvnw.net/jtv_user_pictures/672dc2fd-072c-470e-a6c5-62f37f937682-profile_image-70x70.png"/> UpATree</h1>

<p> </p>
<div class="row">
    <div class="column">
        <h2> Ladder Stats</h2>
        {stat_tab}
    </div>
    <div class="column">
        <h2>Nemeses</h2>
        {nem_tab}
    </div>
</div>

## Games by Race

{r_wrt.to_markdown()}

![Games by Race](./assets/gm_hist.png)

![Sal's MMR](./assets/MMR.png)

![Daily Stats](./assets/daily.png)

![Win Rate vs Time](./assets/r_wrt.png)

'''
with open('./docs/index.md', "r") as f:
    data = f.read()

with open('./docs/index.md',  "w", encoding='utf-8') as f:
    f.write(index)

with open("log.txt", "a") as f:
    t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(f"Writing a log file {t}.\n")



