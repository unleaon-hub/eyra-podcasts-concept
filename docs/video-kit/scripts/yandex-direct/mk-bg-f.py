#!/usr/bin/env python3
"""Concept F: brighten + clean the LEFT light wall to the benchmark's level (its lit wall ≈ rgb(236,228,244), luma ~230;
the edited scenes come out ~155-175). Only pixels left of the wall edge, outside the expert mask and close to the median
wall colour (so tables/props are untouched). Also writes geo.js (wall edge bx, head edge hx).
scenes-f/<id>-16x9-up.jpg + -mask.png -> scenes-f/<id>-16x9.jpg"""
import json, sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter
D = Path(__file__).resolve().parent / 'scenes-f'
src = open(Path(__file__).resolve().parent / 'mk-bg.py').read(); exec(src[src.index('def srgb2lab'):src.index('CROP = {}')])  # Lab helpers from mk-bg.py
G = {}
for e in sys.argv[1:] or ['mira', 'kira', 'asya', 'eva', 'sofia']:
    im = Image.open(D / f'{e}-16x9-up.jpg').convert('RGB'); mm = Image.open(D / f'{e}-16x9-mask.png').convert('L')
    a = np.asarray(im).astype(float); L = a @ [.2126, .7152, .0722]; m = np.asarray(mm) > 100
    c = np.nanmedian(np.where(m[60:380], np.nan, L[60:380]), 0); d = c[8:] - c[:-8]
    bx = int(min(range(500, 1400), key=lambda x: d[x]) + 4); hx = int(np.nonzero(m[:430].any(0))[0].min()); G[e] = {'bx': bx, 'hx': hx}
    lab = srgb2lab(a); ref = np.median(lab[80:600, 40:bx - 60].reshape(-1, 3), 0)
    dist = np.sqrt((((lab - ref) * [0.4, 1, 1]) ** 2).sum(-1))
    w = np.clip(1 - (dist - 10) / 14, 0, 1)                                  # wall-like pixels
    xr = np.clip((bx - 6 - np.arange(1920)) / 6, 0, 1)[None, :]              # left of the edge, hard stop at the edge
    keep = np.asarray(mm.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))).astype(float) / 255
    w = Image.fromarray((w * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(4)); w = np.asarray(w) / 255 * xr * (1 - keep)
    lab2 = lab.copy(); lab2[..., 0] = np.minimum(99, lab[..., 0] + (97 - ref[0]) * 0.5); lab2[..., 1:] *= 0.8   # constant lift keeps the window-light streaks
    out = lab2srgb(lab * (1 - w[..., None]) + lab2 * w[..., None])
    Image.fromarray(out.astype('uint8')).save(D / f'{e}-16x9.jpg', quality=94); print(e, G[e], 'wall', ref.round(1))
open(D / 'geo.js', 'w').write('// bx = light|dark wall edge, hx = head/hair left edge (rows 0-430), px in the 1920 scene\nwindow.GEO=' + json.dumps(G) + ';\n')
