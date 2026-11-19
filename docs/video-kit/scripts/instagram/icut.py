#!/usr/bin/env python3
# EYRA · person cut-outs for the bold colour-field cards (meet / pinned): cut-<id>.png (RGBA) + cut.js
# Uses the square scenes and their person masks (../template/work). Only needed to rebuild; ready files ship with the scripts.
import json
import numpy as np
from PIL import Image, ImageFilter
import live
out = {}
for e in live.es:
    im = Image.open(live.W + e + '-1x1-up.jpg').convert('RGB')
    m = Image.open(live.W + e + '-1x1-mask.png').convert('L').filter(ImageFilter.GaussianBlur(0.9))
    a = np.asarray(m) > 20; ys, xs = np.nonzero(a)
    x0, x1, y0 = int(xs.min()), int(xs.max()) + 1, int(ys.min())
    rgba = im.copy(); rgba.putalpha(m); rgba = rgba.crop((x0, y0, x1, 1280))
    rgba.save(f'cut-{e}.png', optimize=True)
    fx, fy, fw, fh = live.F[e]
    out[e] = {'w': x1 - x0, 'h': 1280 - y0, 'fcx': round(fx + fw / 2 - x0), 'fy': round(fy - y0), 'fh': fh}
    print(e, out[e])
open('cut.js', 'w').write('window.CUT=' + json.dumps(out) + ';\n')
