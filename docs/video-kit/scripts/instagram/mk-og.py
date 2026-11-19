#!/usr/bin/env python3
"""Prepare 1200x630 backgrounds for Threads/link-preview cards (og modes in ig.html).
Experts: clean 16:9 scene from ../template/work/<id>-16x9-up.jpg (kit) — zoomed, expert pushed to the side opposite the card.
Home: centre plate of the pinned triptych (plate-pin-C.jpg)."""
import json
from pathlib import Path
from PIL import Image, ImageFilter
H=Path(__file__).resolve().parent
SRC=H.parent/'template'/'work'
if not SRC.exists(): SRC=H.parent.parent/'EYRA-video-kit'/'scripts'/'template'/'work'
import numpy as np
side={}
for e in 'alisa asya eva kira lera maya mira nika sofia vera'.split():
    im=Image.open(SRC/f'{e}-16x9-up.jpg').convert('RGB'); s=0.72; w,h=round(1920*s),round(1080*s)
    m=np.asarray(Image.open(SRC/f'{e}-16x9-mask.png').convert('L').resize(im.size))>128
    ys,xs=np.nonzero(m); fx=xs.mean()/m.shape[1]; fy=ys.min()/m.shape[0]   # expert centre x and head top
    im=im.resize((w,h),Image.LANCZOS); L=fx<.5  # expert on the left -> card on the right
    want=(.29 if L else .72)*1200; off=int(min(max(fx*w-want,0),w-1200)); top=int(min(max(fy*h-40,0),h-630))
    im.crop((off,top,off+1200,top+630)).filter(ImageFilter.UnsharpMask(1,30,2)).save(H/f'bg-og-{e}.jpg',quality=90)
    side[e]='R' if L else 'L'; print(e,'card',side[e],'expert at',round((fx*w-off)/1200,2))
c=Image.open(H/'plate-pin-C.jpg').convert('RGB'); c=c.resize((1200,1500),Image.LANCZOS)
c.crop((0,760,1200,1390)).save(H/'bg-og-home.jpg',quality=90)
(H/'ogside.js').write_text('window.OGSIDE='+json.dumps(side)+';\n')
