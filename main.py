# -*- coding: utf-8 -*-
import requests
from PIL import Image
import io
import os

import pandas as pd

from time import gmtime, strftime

import sc2_stats

sc2_stats.c_dat['c_id'] = os.environ['C_ID']
sc2_stats.c_dat['s_id'] = os.environ['S_ID']

u_dat = sc2_stats.c_dat

tk = sc2_stats.bliz_token(u_dat['c_id'],u_dat['s_id'])


ladders = ['1v1','2v2','3v3','4v4']

player_lad = [s for s in ladders if s in u_dat.keys()]

tk = sc2_stats.bliz_token(u_dat['c_id'],u_dat['s_id'])

tk_header = {'Authorization': f'Bearer {tk}'}

pp = sc2_stats.sc2_profile(u_dat['1v1']['server'],
                 u_dat['1v1']['region'],
                 u_dat['1v1']['realm'],
                 u_dat['1v1']['sc2id'],
                 tk_header) 

ll = sc2_stats.sc2_ladsum(u_dat['1v1']['server'],
                 u_dat['1v1']['region'],
                 u_dat['1v1']['realm'],
                 u_dat['1v1']['sc2id'],
                 tk_header,
                 ladder=player_lad[0]) 

lspc = sc2_stats.sc2_ladspc(u_dat['1v1']['server'],
                 u_dat['1v1']['region'],
                 u_dat['1v1']['realm'],
                 u_dat['1v1']['sc2id'],
                 ll['ladder_id'],
                 tk_header)

mhs = sc2_stats.sc2_match(u_dat['1v1']['server'],
                 u_dat['1v1']['region'],
                 u_dat['1v1']['realm'],
                 u_dat['1v1']['sc2id'],
                 tk_header)

# load subathon google sheet
# and read the game columns
sheet = 'https://docs.google.com/spreadsheets/d/17faRtX9jtmRXzynJ9QJBIiR_2vlsT7e8k3F526NDA7k/export?format=csv&gid=710961897#gid=710961897'

df = pd.read_csv(sheet, usecols=[8,9,10,11,12,13,14,15,16,17,18,19,20,21,22])

# create MMR plot and save it to assets
df.plot(y="Sal's MMR").get_figure().savefig('./docs/assets/MMR.png')

# Daily Stats
win_d = df.groupby('Day')['Win?'].sum()
win_d.name='W'
loss_d = df[df['Win?']==0].groupby('Day')['Win?'].count()
loss_d.name='L'

day_df = pd.concat([win_d,loss_d], axis=1)
day_df.plot.bar(stacked=True, color={'W':'dodgerblue', 'L':'darkorange'}).get_figure().savefig('./docs/assets/daily.png')

# create first table
t1 = pd.DataFrame([df.shape[0],
                   df.loc[df['ΔMMR'] > 0,"ΔMMR"].sum(),
                   abs(df.loc[df['ΔMMR'] < 0,"ΔMMR"].sum()),
                   df['Sal\'s MMR'].max(),
                   df['Sal\'s MMR'].min(),
                   df['Win Streak'].max(),
                   df['Loss Streak'].max(),
                   df['MMR'].max(),
                   df['MMR'].min(),
                   ], 
                   columns=['Stats'],
                   index=['Matches Played','MMR Gained', 'MMR lost', 'Max MMR', 'Min MMR',
                          'Longest Win Streak', 'Longest Loss Streak', 'Highest MMR Beaten',
                          'Lowest MMR Thrown to'])

# create nemesis table
nem = df[df['ΔMMR']>0].groupby('Opponent').sum()['ΔMMR'].sort_values(ascending=False)[0:6]

# create main page
index = f'''---
layout: home
---

## UpATree Ladder Stats

{t1.to_markdown()}

{nem.to_markdown()}

![Sal's MMR](./assets/MMR.png)

![Daily Stats](./assets/daily.png)

'''
with open('./docs/index.md', "r") as f:
    data = f.read()

with open('./docs/index.md',  "w") as f:
    f.write(index)

with open("log.txt", "a") as f:
    t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(f"Writing a log file {t}.\n")



