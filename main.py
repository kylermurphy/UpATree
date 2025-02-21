# -*- coding: utf-8 -*-
import requests
from PIL import Image
import io


imgUrl = 'https://static.starcraft2.com/starport/bda9a860-ca36-11ec-b5ea-4bed4e205979/portraits/3-19.jpg'
r = requests.get(imgUrl, stream=True)
img = Image.open(io.BytesIO(r.content))

img.save('test.jpg')

