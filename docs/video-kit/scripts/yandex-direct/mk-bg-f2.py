#!/usr/bin/env python3
"""Concept F2: F scenes with a deeper back wall so the expert pops.
- left light wall: constant lift (keeps window streaks) + per-expert paleness (Mira lilac, Sofia lime -> airier, toward the benchmark)
- dark zone (right of the wall edge, outside the expert): deeper (keeps hue), highlights of art/plant/prop compressed so they
  recede, soft falloff away from the expert's head (vignette)
- expert: very slight lift + subtle rim light on the head/hair edge facing the window (left)
Ася: face restored from the kit scene (affine-aligned, colour-matched, feathered ellipse) -> scenes-f2/asya-16x9-up.jpg
In: scenes-f2/<id>-16x9-up.jpg if present else scenes-f/, masks from scenes-f/. Out: scenes-f2/<id>-16x9.jpg + geo.js"""
import json, sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter
H = Path(__file__).resolve().parent; F1 = H / 'scenes-f'; D = H / 'scenes-f2'
src = open(H / 'mk-bg.py').read(); exec(src[src.index('def srgb2lab'):src.index('CROP = {}')])  # Lab helpers
P = json.load(open(D / 'params.json'))
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float) / 255
G = {}
for e in sys.argv[1:] or ['mira', 'kira', 'asya', 'eva', 'sofia']:
    p = {**P['default'], **P.get(e, {})}
    up = D / f'{e}-16x9-up.jpg'; up = up if up.exists() else F1 / f'{e}-16x9-up.jpg'
    a = np.asarray(Image.open(up).convert('RGB')).astype(float); mm = Image.open(F1 / f'{e}-16x9-mask.png').convert('L'); m0 = np.asarray(mm) / 255
    L = a @ [.2126, .7152, .0722]; m = m0 > .4
    c = np.nanmedian(np.where(m[60:380], np.nan, L[60:380]), 0); d = c[8:] - c[:-8]
    bx = int(min(range(500, 1400), key=lambda x: d[x]) + 4); ys, xs = np.nonzero(m[:430]); hx = int(xs.min()); G[e] = {'bx': bx, 'hx': hx}
    hcx, hcy = xs.mean(), ys.mean()
    lab = srgb2lab(a); out = lab.copy()
    keep = blur(np.asarray(mm.filter(ImageFilter.MaxFilter(5))) / 255, 2.5)
    X = np.arange(1920)[None, :]; Y = np.arange(1080)[:, None]
    # 1 light wall
    ref = np.median(lab[80:600, 40:bx - 60].reshape(-1, 3), 0)
    # pass 2: classify the edge band (bx±30) per pixel by brightness, so the wall corner leaves no grey strip
    dref = np.median(lab[80:500, bx + 30:bx + 140][~m[80:500, bx + 30:bx + 140]].reshape(-1, 3), 0); mid = (ref[0] + dref[0]) / 2
    # pass 3: the edits leave a pale 6-14px wall-return strip at the corner; continue the light wall up to the true edge
    for y in range(min(1080, p['floor'])):
        row = lab[y, bx - 30:bx + 40, 0]; dk_ = np.nonzero(row < mid)[0]
        if not len(dk_): continue
        ed = bx - 30 + dk_[0]
        if m[y, ed - 40:ed].any(): continue
        lab[y, ed - 16:ed] = lab[y, ed - 34:ed - 18]
    out = lab.copy()
    isd = (X > bx + 30) | ((X > bx - 30) & (lab[..., 0] < mid)); isd = blur(isd.astype(float), 1.2)
    floor = np.clip((p['floor'] - Y) / 30, 0, 1)                                    # dark-zone treatment stops at the table/floor line
    dist = np.sqrt((((lab - ref) * [0.4, 1, 1]) ** 2).sum(-1)); w = blur(np.clip(1 - (dist - 10) / 14, 0, 1), 4) * (1 - isd) * (X < bx + 30) * (1 - keep)
    lw = lab.copy(); lw[..., 0] = np.minimum(99, lab[..., 0] + (97 - ref[0]) * p['lift']); lw[..., 1:] *= p['pale']
    out = out * (1 - w[..., None]) + lw * w[..., None]
    # 2 dark zone
    dz = isd * floor * (1 - keep)
    r = np.sqrt(((X - hcx) / 1100.) ** 2 + ((Y - hcy) / 800.) ** 2)
    fall = 1 - p['vig'] * np.clip(r - .25, 0, 1) ** 1.3
    Ld = lab[..., 0] * p['deep'] - np.maximum(0, lab[..., 0] - 45) * p['hi']
    dk = lab.copy(); dk[..., 0] = np.maximum(2, Ld * fall); dk[..., 1:] *= p['chroma']
    out = out * (1 - dz[..., None]) + dk * dz[..., None]
    # 3 expert: slight lift + rim on the left (window) edge of head/shoulders
    out[..., 0] = out[..., 0] + (100 - out[..., 0]) * p['elift'] * m0
    er = np.asarray(mm.filter(ImageFilter.MinFilter(p['rimw'] | 1))) / 255
    band = np.clip(m0 - er, 0, 1); band = blur(band, 3) * np.clip((hcx + 80 - X) / 250, 0, 1) * np.clip((700 - Y) / 300, 0, 1)
    out[..., 0] += p['rim'] * band; out[..., 1] += 2 * band; out[..., 2] += 5 * band   # warm rim
    Image.fromarray(lab2srgb(out).astype('uint8')).save(D / f'{e}-16x9.jpg', quality=94); print(e, G[e], flush=True)
geo = json.loads(open(D / 'geo.js').read().split('window.GEO=', 1)[1].strip().rstrip(';')) if (D / 'geo.js').exists() else {}
geo.update(G); open(D / 'geo.js', 'w').write('// bx = light|dark wall edge, hx = head/hair left edge (rows 0-430), px in the 1920 scene\nwindow.GEO=' + json.dumps(geo) + ';\n')
