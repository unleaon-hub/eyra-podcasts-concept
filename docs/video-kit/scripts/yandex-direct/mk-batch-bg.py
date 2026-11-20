#!/usr/bin/env python3
"""Yandex Direct batch (F2 system): build the 2 scene variants per expert and apply the F2 grade.
 A = scenes-f/<id>-16x9-up.jpg (+mask)        two-zone edit of the kit scene
 B = scenes-f/<id>-b-src.jpg                   same room, other artwork / prop / window light; the expert pixels are
     replaced by A's expert (B aligned to A by ORB+affine on the expert) so the face is identical in both
 Ася: face in A restored from the kit scene (aligned, kit contrast kept, only mean colour shifted to the scene light)
 F2 grade (as concepts/F2-darker): paler light wall, deeper back wall with dimmed art + falloff, expert lift + warm rim,
 clean wall edge. Out: batch/scenes/<id>-<a|b>.jpg, <id>-mask.png, batch/geo.js"""
import json, sys
import cv2, numpy as np
from pathlib import Path
from PIL import Image, ImageFilter
H = Path(__file__).resolve().parent; F1 = H / 'scenes-f'; O = H / 'batch' / 'scenes'; O.mkdir(parents=True, exist_ok=True); KIT = H.parent / 'template' / 'work'
src = open(H / 'mk-bg.py').read(); exec(src[src.index('def srgb2lab'):src.index('CROP = {}')])  # Lab helpers
P = json.load(open(H / 'batch' / 'params.json'))
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float) / 255
def align(src_bgr, dst_bgr, ms, md):
    o = cv2.ORB_create(8000)
    ka, da = o.detectAndCompute(cv2.cvtColor(src_bgr, cv2.COLOR_BGR2GRAY), ms); kb, db = o.detectAndCompute(cv2.cvtColor(dst_bgr, cv2.COLOR_BGR2GRAY), md)
    mt = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db), key=lambda m: m.distance)[:800]
    M, inl = cv2.estimateAffinePartial2D(np.float32([ka[m.queryIdx].pt for m in mt]), np.float32([kb[m.trainIdx].pt for m in mt]), method=cv2.RANSAC, ransacReprojThreshold=4)
    return M, int(inl.sum()), len(mt)
def asya_face(A, mA):
    K = cv2.imread(str(KIT / 'asya-16x9-up.jpg')); mK = cv2.imread(str(KIT / 'asya-16x9-mask.png'), 0)
    M, n, t = align(K, A, (mK > 128).astype('uint8') * 255, (mA > 128).astype('uint8') * 255); print('asya face align', n, '/', t)
    Kw = cv2.warpAffine(K, M, (1920, 1080), flags=cv2.INTER_LANCZOS4).astype(np.float32)
    m = np.zeros((1080, 1920), np.float32); cv2.ellipse(m, (1200, 380), (138, 178), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 16)[..., None]
    sel = m[..., 0] > .5; Af = A.astype(np.float32)
    for c in range(3): Kw[..., c] += (Af[..., c][sel].mean() - Kw[..., c][sel].mean()) * 0.7   # kit contrast kept, light colour matched
    return np.clip(Af * (1 - m) + Kw * m, 0, 255).astype('uint8')
def grade(a, mm, p):
    a = a.astype(float); m0 = np.asarray(mm) / 255; m = m0 > .4; L = a @ [.2126, .7152, .0722]
    c = np.nanmedian(np.where(m[60:380], np.nan, L[60:380]), 0); d = c[8:] - c[:-8]; d = np.nan_to_num(d, nan=0)
    bx = int(min(range(500, 1400), key=lambda x: d[x]) + 4); ys, xs = np.nonzero(m[:430]); hx = int(xs.min()); hxr = int(xs.max()); hcx, hcy = xs.mean(), ys.mean()
    lab = srgb2lab(a); X = np.arange(1920)[None, :]; Y = np.arange(1080)[:, None]
    keep = blur(np.asarray(mm.filter(ImageFilter.MaxFilter(5))) / 255, 2.5)
    ref = np.median(lab[80:600, 40:bx - 60].reshape(-1, 3), 0)
    dref = np.median(lab[80:500, bx + 30:bx + 140][~m[80:500, bx + 30:bx + 140]].reshape(-1, 3), 0); mid = (ref[0] + dref[0]) / 2
    for y in range(min(1080, p['floor'])):                      # continue the light wall up to the true edge (no pale corner strip)
        dk_ = np.nonzero(lab[y, bx - 30:bx + 40, 0] < mid)[0]
        if not len(dk_): continue
        ed = bx - 30 + dk_[0]
        if m[y, ed - 40:ed].any(): continue
        lab[y, ed - 16:ed] = lab[y, ed - 34:ed - 18]
    out = lab.copy()
    isd = blur(((X > bx + 30) | ((X > bx - 30) & (lab[..., 0] < mid))).astype(float), 1.2); floor = np.clip((p['floor'] - Y) / 30, 0, 1)
    dist = np.sqrt((((lab - ref) * [0.4, 1, 1]) ** 2).sum(-1)); w = blur(np.clip(1 - (dist - 10) / 14, 0, 1), 4) * (1 - isd) * (X < bx + 30) * (1 - keep)
    lw = lab.copy(); lw[..., 0] = np.minimum(99, lab[..., 0] + (97 - ref[0]) * p['lift']); lw[..., 1:] *= p['pale']; out = out * (1 - w[..., None]) + lw * w[..., None]
    dz = isd * floor * (1 - keep); r = np.sqrt(((X - hcx) / 1100.) ** 2 + ((Y - hcy) / 800.) ** 2); fall = 1 - p['vig'] * np.clip(r - .25, 0, 1) ** 1.3
    dk = lab.copy(); dk[..., 0] = np.maximum(2, (lab[..., 0] * p['deep'] - np.maximum(0, lab[..., 0] - 45) * p['hi']) * fall); dk[..., 1:] *= p['chroma']
    out = out * (1 - dz[..., None]) + dk * dz[..., None]
    out[..., 0] += (100 - out[..., 0]) * p['elift'] * m0
    er = np.asarray(mm.filter(ImageFilter.MinFilter(p['rimw'] | 1))) / 255
    band = blur(np.clip(m0 - er, 0, 1), 3) * np.clip((hcx + 80 - X) / 250, 0, 1) * np.clip((700 - Y) / 300, 0, 1)
    out[..., 0] += p['rim'] * band; out[..., 1] += 2 * band; out[..., 2] += 5 * band
    yb = np.nonzero(m.any(1))[0]; fx = np.nonzero(m[max(0, int(hcy) - 90):int(hcy) + 90].any(0))[0]
    return lab2srgb(out).astype('uint8'), {'bx': bx, 'hx': hx, 'hxr': hxr, 'hcx': int(hcx), 'hcy': int(hcy), 'top': int(yb.min()), 'fxl': int(fx.min()), 'fxr': int(fx.max())}
G = json.loads((H / 'batch' / 'geo.js').read_text().split('window.GEO=', 1)[1].strip().rstrip(';')) if (H / 'batch' / 'geo.js').exists() else {}
for e in sys.argv[1:] or ['mira', 'kira', 'asya', 'eva', 'sofia', 'lera', 'vera', 'nika', 'maya', 'alisa']:
    p = {**P['default'], **P.get(e, {})}
    A = cv2.imread(str(F1 / f'{e}-16x9-up.jpg')); mA = cv2.imread(str(F1 / f'{e}-16x9-mask.png'), 0)
    if e == 'asya': A = asya_face(A, mA)
    Bs = cv2.resize(cv2.imread(str(F1 / f'{e}-b-src.jpg')), (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
    mb = (cv2.resize(mA, (1920, 1080)) > 128).astype('uint8') * 255
    M, n, t = align(Bs, A, mb, (mA > 128).astype('uint8') * 255); Bw = cv2.warpAffine(Bs, M, (1920, 1080), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    k = cv2.GaussianBlur(cv2.dilate((mA > 100).astype(np.float32), np.ones((7, 7))), (0, 0), 3)[..., None]
    B = np.clip(Bw * (1 - k) + A * k, 0, 255).astype('uint8')
    mm = Image.fromarray(mA); Image.fromarray(mA).save(O / f'{e}-mask.png')
    for v, img in (('a', A), ('b', B)):
        out, g = grade(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), mm, p); Image.fromarray(out).save(O / f'{e}-{v}.jpg', quality=94); G[f'{e}-{v}'] = g
    print(e, 'B align', n, '/', t, 'scale', round(float(np.hypot(*M[0, :2])), 3), G[f'{e}-a'], flush=True)
    (H / 'batch' / 'geo.js').write_text('// per scene: bx wall edge, hx/hxr head band (rows 0-430) left/right, fxl/fxr mask extent at face level (hcy±90), hcx/hcy head centre, top = top of the expert (1920x1080 px)\nwindow.GEO=' + json.dumps(G) + ';\n')
