# Dzen «Ролики»: vertical 1080x1920 backgrounds. Per-expert scale so every head top lands at ~y 800, photo bottom-aligned, wall extended upward.
import json,sys
import numpy as np
from PIL import Image
sys.argv=[sys.argv[0]]+sys.argv[1:]
from live import bg,es,W
M={}
for e in es:
  m=np.asarray(Image.open(W+e+'-1x1-mask.png').convert('L'))>128;M[e]=int(np.nonzero(m.any(1))[0].min())
HEAD=800;out={}
for e in es:
  s=(1920-HEAD)/(1280-M[e]);s=max(0.95,min(1.3,s))
  im,T=bg(e,s=s);im.save(f'vbg-{e}.jpg',quality=95)
  out[e]={'s':round(s,4),'T':T,'head':round(T+s*M[e])};print(e,out[e])
json.dump(out,open('vbg.json','w'))
