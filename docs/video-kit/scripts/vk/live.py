# VK live cover: python3 lock.py 120 && python3 live.py  -> slide-<id>.png (1080x1920); python3 kb.py -> live-cover.mp4
# VK live cover slides 1080x1920 from the square scenes: scale 1.2, face-centred crop, top extended as soft wall
import json,sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import os
HERE=os.path.dirname(os.path.abspath(__file__));os.chdir(HERE)
W=os.path.join(HERE,'..','template','work')+'/'
F=json.load(open('faces1.json'));es='asya kira vera lera mira nika eva maya sofia alisa'.split()
CW,CH=1080,1920;LY=300
def bg(e,s=1.2,over=0):
  im=Image.open(W+e+'-1x1-up.jpg').convert('RGB');x,y,w,h=F[e];fcx=x+w/2
  sw=CW/s;x0=min(max(fcx-sw/2,0),1280-sw)
  H=round(1280*s);crop=im.crop((round(x0),0,round(x0+sw),1280)).resize((CW,H),Image.LANCZOS)
  crop=crop.filter(ImageFilter.UnsharpMask(radius=1.6,percent=45,threshold=2))
  T=CH-H+over
  can=np.zeros((CH,CW,3),np.float32);a=np.asarray(crop,np.float32)
  # top extension: per-column colour of the top band, heavily blurred, lifted slightly toward the top (sunlit wall)
  band=a[:40].mean(0)                                   # (CW,3)
  ext=np.repeat(band[None],T+200,0)
  e_im=Image.fromarray(ext.clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))
  ext=np.asarray(e_im,np.float32)
  g=np.linspace(1.035,1.0,T+200)[:,None,None];ext=ext*g
  can[:T+200]=ext
  # feather image over extension
  al=np.ones((H,1,1),np.float32);fe=150;al[:fe,0,0]=np.linspace(0,1,fe)**1.2
  seg=can[T:T+H];can[T:T+H]=seg*(1-al)+a*al if True else a
  out=Image.fromarray(can.clip(0,255).astype(np.uint8))
  # tiny grain to hide banding in the extension
  rng=np.random.default_rng(7);n=rng.normal(0,1.6,(CH,CW,1)).astype(np.float32)
  o=np.asarray(out,np.float32);o[:T+60]+=n[:T+60];out=Image.fromarray(o.clip(0,255).astype(np.uint8))
  return out,T
def slide(e,lock=True):
  im,T=bg(e)
  if lock:
    L=Image.open('lock-120.png').convert('RGBA');a=L.split()[3].point(lambda v:int(v*0.86));L.putalpha(a)
    im.paste(L,((CW-L.width)//2,LY),L)
  return im,T
if __name__=='__main__':
  for e in (sys.argv[1:] or es):
    im,T=slide(e);im.save(f'slide-{e}.png');print(e,'T',T)
