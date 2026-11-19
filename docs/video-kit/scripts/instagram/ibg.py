#!/usr/bin/env python3
# EYRA · Instagram backgrounds from the square scenes (../template/work): head top lands exactly at HEAD.
# post 1080x1350 (head 520), story 1080x1920 (head 1050), reels 1080x1920 (head 900).
# If the scene is already full width, it is shifted down and the bottom edge is cropped instead.
# Also writes round face crops face-<id>.png for quote cards. Only needed to rebuild; the ready files ship with the scripts.
import json
import numpy as np
from PIL import Image, ImageDraw
import live
KINDS={'post':(1080,1350,520),'story':(1080,1920,1050),'reels':(1080,1920,900)}
M={}
for e in live.es:
  m=np.asarray(Image.open(live.W+e+'-1x1-mask.png').convert('L'))>128;M[e]=int(np.nonzero(m.any(1))[0].min())
out={}
for k,(W,H,HEAD) in KINDS.items():
  out[k]={}
  for e in live.es:
    s=(H-HEAD)/(1280-M[e]);s=max(W/1280,min(1.25,s))
    head0=H-s*(1280-M[e]);over=max(0,round(HEAD-head0))
    live.CW,live.CH=W,H+over
    im,T=live.bg(e,s=s);im=im.crop((0,0,W,H));im.save(f'bg-{k}-{e}.jpg',quality=95)
    out[k][e]={'s':round(s,3),'head':round(T+s*M[e]),'cut':over}
  print(k,out[k])
json.dump(out,open('ibg.json','w'))
# face crops
for e in live.es:
  x,y,w,h=live.F[e];cx,cy=x+w/2,y+h*0.52;r=max(w,h)*0.95
  im=Image.open(live.W+e+'-1x1-up.jpg').convert('RGB').crop((round(cx-r),round(cy-r),round(cx+r),round(cy+r))).resize((400,400),Image.LANCZOS)
  mk=Image.new('L',(1600,1600),0);ImageDraw.Draw(mk).ellipse((0,0,1599,1599),fill=255);mk=mk.resize((400,400),Image.LANCZOS)
  im.putalpha(mk);im.save(f'face-{e}.png')
