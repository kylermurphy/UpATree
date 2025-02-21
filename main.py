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

tk = bliz_token(u_dat['c_id'],u_dat['s_id'])

imgUrl = 'https://static.starcraft2.com/starport/bda9a860-ca36-11ec-b5ea-4bed4e205979/portraits/3-19.jpg'
r = requests.get(imgUrl, stream=True)
img = Image.open(io.BytesIO(r.content))

img.save('test.jpg')



with open("file.txt", "a") as f:
    t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(f"Writing a log file {t}, {tk}.")



