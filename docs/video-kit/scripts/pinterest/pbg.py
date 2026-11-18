#!/usr/bin/env python3
# EYRA · Pinterest: 2:3 backgrounds (1000x1500) from the square scenes in ../template/work.
# Every head top lands exactly at HEAD: a=700 (pins), b=640 (board covers). Where the scene is already full-width
# (scale can't go lower), it is shifted down and the bottom edge of the table is cropped instead.
# Only needed to rebuild pbga-*.jpg / pbgb-*.jpg; new-pin.py uses the ready backgrounds.
import json,sys
import numpy as np
from PIL import Image
import live
HEADS={'a':700,'b':640}
M={}
for e in live.es:
  m=np.asarray(Image.open(live.W+e+'-1x1-mask.png').convert('L'))>128;M[e]=int(np.nonzero(m.any(1))[0].min())
out={}
for kind,HEAD in HEADS.items():
  out[kind]={}
  for e in live.es:
    s=(1500-HEAD)/(1280-M[e]);s=max(1000/1280,min(1.25,s))
    head0=1500-s*(1280-M[e]);over=max(0,round(HEAD-head0))
    live.CW,live.CH=1000,1500+over
    im,T=live.bg(e,s=s);im=im.crop((0,0,1000,1500));im.save(f'pbg{kind}-{e}.jpg',quality=95)
    out[kind][e]={'s':round(s,3),'head':round(T+s*M[e]),'cut':over}
  print(kind,out[kind])
json.dump(out,open('pbg.json','w'))
