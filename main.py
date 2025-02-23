# -*- coding: utf-8 -*-
import requests
from PIL import Image
import io
import os

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

imgUrl = 'https://static.starcraft2.com/starport/bda9a860-ca36-11ec-b5ea-4bed4e205979/portraits/3-19.jpg'
r = requests.get(imgUrl, stream=True)
img = Image.open(io.BytesIO(r.content))

img.save('test.jpg')



with open("log.txt", "a") as f:
    t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(f"Writing a log file {t}.\n")



