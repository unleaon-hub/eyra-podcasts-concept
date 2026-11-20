#!/usr/bin/env python3
"""Backgrounds for concept E (benchmark layout): the expert's own sunlit scene, cropped so the
left side is a clean wall, wall tinted in the expert's accent (Lab chroma), slightly brighter light.
Writes bg/<id>-<fmt>.jpg for fmt in 4x3 (1440x1080), 16x9 (1920x1080), 1x1 (1080x1080) + bg/crop.js (crop offset, head/hair left edge (rows 0-430); line 2 may overlap shoulders like the benchmark)."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
HERE = Path(__file__).resolve().parent; W = HERE.parent / 'template' / 'work'; OUT = HERE / 'bg'; OUT.mkdir(exist_ok=True)
S = open(HERE.parent / 'instagram' / 'site.js', encoding='utf-8').read(); SITE = json.loads(S.split('window.SITE=')[1].split(';\nwindow.OFFER=')[0])
def srgb2lab(c):
    c = c / 255.0; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = c @ M.T / np.array([0.95047, 1, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def lab2srgb(l):
    fy = (l[..., 0] + 16) / 116; fx = fy + l[..., 1] / 500; fz = fy - l[..., 2] / 200
    f = np.stack([fx, fy, fz], -1); xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1, 1.08883])
    M = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]]); c = xyz @ M.T
    c = np.where(c > 0.0031308, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055, 12.92 * c); return np.clip(c * 255, 0, 255)
CROP = {}
def make(e, fmt):
    src = '16x9' if fmt != '1x1' else '1x1'; base = HERE / 'scenes' if (HERE / 'scenes' / f'{e}-{src}-up.jpg').exists() else W  # props-free scene if present
    im = Image.open(base / f'{e}-{src}-up.jpg').convert('RGB'); m = Image.open(base / f'{e}-{src}-mask.png').convert('L')
    if fmt == '4x3':
        mk = np.asarray(m) > 128; up = mk[:int(.62 * mk.shape[0])]; xs = np.nonzero(up.any(0))[0]; x0 = xs.min()
        band = mk[:int(.25 * mk.shape[0])]; fx = np.nonzero(band.any(0))[0].mean()      # head centre
        off = int(min(max(x0 - 640, fx - 0.68 * 1440, 0), 480)); off = int(min(off, x0 - 600)) if x0 - 600 > 0 else 0; box = (off, 0, off + 1440, 1080); im = im.crop(box); m = m.crop(box)
        hb = np.asarray(m)[0:430] > 100; CROP[e] = {'off': off, 'x0head': int(np.nonzero(hb.any(0))[0].min()) if hb.any() else 1440}  # head/hair left edge (rows 0-430); line 2 may overlap shoulders like the benchmark
    elif fmt == '1x1': im = im.resize((1080, 1080), Image.LANCZOS); m = m.resize((1080, 1080))
    a = np.asarray(im).astype(float); lab = srgb2lab(a)
    acc = srgb2lab(np.array([[int(SITE[e]['accent'][i:i + 2], 16) for i in (1, 3, 5)]], float))[0]
    keep = np.asarray(m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(3))).astype(float) / 255      # expert stays untouched
    chroma = np.hypot(lab[..., 1], lab[..., 2]); neutral = np.clip(1 - chroma / 28, 0, 1)  # only near-neutral wall / light
    bright = np.clip((lab[..., 0] - 35) / 40, 0, 1)
    w = (1 - keep) * neutral * bright
    k = 1.25  # richer than the pastel site accent
    lab[..., 1] = lab[..., 1] * (1 - w) + acc[1] * k * w; lab[..., 2] = lab[..., 2] * (1 - w) + acc[2] * k * w
    lab[..., 0] = lab[..., 0] + (100 - lab[..., 0]) * 0.10 * (1 - keep)               # cleaner, brighter light on the wall
    out = lab2srgb(lab); out = out * (1 - keep[..., None]) + np.clip(a * 1.03 + 2, 0, 255) * keep[..., None]
    Image.fromarray(out.astype('uint8')).save(OUT / f'{e}-{fmt}.jpg', quality=93)
E = sys.argv[1:] or ['asya', 'lera', 'mira', 'kira', 'sofia']
for e in E:
    for f in ('4x3', '16x9', '1x1'): make(e, f)
    print(e, CROP.get(e))
open(OUT / 'crop.js', 'w').write('window.CROP=' + json.dumps(CROP) + ';\n')
