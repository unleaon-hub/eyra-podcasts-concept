#!/usr/bin/env python3
"""Concept sheets: comparison of A–D, old (reference/) vs concepts, real-size legibility check.
Usage: python3 sheets.py   (reads ../../yandex-direct/concepts, writes ../../yandex-direct/previews)"""
import glob, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; D = HERE.parents[1] / 'yandex-direct'; C = D / 'concepts'; PV = D / 'previews'; PV.mkdir(parents=True, exist_ok=True)
F = lambda s, b=True: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
NAMES = {'A': 'A · Солнечная сцена', 'B': 'B · Цветной акцент', 'C': 'C · Разговор в Telegram', 'D': 'D · Крупный портрет'}
EX = ['asya', 'lera', 'mira']
def get(c, e, tag): return Image.open(glob.glob(str(C / f'{c}-*' / f'{e}-{c}-{tag}-*'))[0]).convert('RGB')
# 1) comparison: rows = concepts, cols = 3 experts at 4:3 + Asya 1:1 + Asya 16:9
h = 270; cols = [('asya', '4x3'), ('lera', '4x3'), ('mira', '4x3'), ('asya', '1x1'), ('mira', '16x9')]
ws = [round(h * {'4x3': 4 / 3, '1x1': 1, '16x9': 16 / 9}[t]) for _, t in cols]; Wt = 260 + sum(ws) + 14 * len(ws)
S = Image.new('RGB', (Wt, 70 + 4 * (h + 16)), '#f6f2ec'); d = ImageDraw.Draw(S)
d.text((20, 20), 'EYRA · Яндекс Директ — 4 светлых концепта (4:3 · 1:1 · 16:9)', fill='#1d1f1a', font=F(30))
for r, c in enumerate('ABCD'):
    y = 70 + r * (h + 16); d.text((20, y + h // 2 - 30), NAMES[c].replace(' · ', '\n').replace(' в ', '\nв '), fill='#1d1f1a', font=F(21))
    x = 260
    for (e, t), w in zip(cols, ws): S.paste(get(c, e, t).resize((w, h), Image.LANCZOS), (x, y)); x += w + 14
S.save(PV / 'concepts-comparison.jpg', quality=88)
# 2) old vs concepts: left = reference originals (if present) else placeholder, right = A–D at 4:3
REF = {'asya': ['ref-1-asya-night.png', 'ref-2-asya-cafe.png'], 'lera': ['ref-3-lera-pink.png', 'ref-4-lera-split.png'], 'mira': ['ref-5-mira-purple.png', 'ref-6-mira-lilac.png']}
h = 240; w = 320; S = Image.new('RGB', (40 + 2 * (w + 12) + 30 + 4 * (w + 12), 70 + 3 * (h + 46)), '#f6f2ec'); d = ImageDraw.Draw(S)
d.text((20, 18), 'Было (текущие креативы)                                   Стало — концепты A · B · C · D', fill='#1d1f1a', font=F(26))
for r, e in enumerate(EX):
    y = 70 + r * (h + 46); x = 20
    for f in REF[e]:
        p = D / 'reference' / f
        if p.exists(): S.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (x, y))
        else: d.rectangle((x, y, x + w, y + h), fill='#e4ded5'); d.text((x + 20, y + h // 2 - 10), 'положите ' + f + '\nв reference/', fill='#6b675f', font=F(15, False))
        x += w + 12
    x += 30
    for c in 'ABCD': S.paste(get(c, e, '4x3').resize((w, h), Image.LANCZOS), (x, y)); d.text((x, y + h + 6), NAMES[c], fill='#57594f', font=F(16, False)); x += w + 12
S.save(PV / 'old-vs-concepts.jpg', quality=88)
# 3) real size: 1:1 at 300 px, 4:3 at 320x240, 16:9 at 400x225 (1x, as in RSYa / feed)
S = Image.new('RGB', (40 + 4 * 420, 60 + 3 * 330), '#ffffff'); d = ImageDraw.Draw(S)
d.text((20, 14), 'Реальный размер показа (1x): 1:1 — 300 px, 4:3 — 320×240, 16:9 — 400×225 · Ася', fill='#1d1f1a', font=F(22))
for i, c in enumerate('ABCD'):
    x = 20 + i * 420; d.text((x, 44), NAMES[c], fill='#57594f', font=F(18, False))
    S.paste(get(c, 'asya', '1x1').resize((300, 300), Image.LANCZOS), (x, 70))
    S.paste(get(c, 'asya', '4x3').resize((320, 240), Image.LANCZOS), (x, 390))
    S.paste(get(c, 'asya', '16x9').resize((400, 225), Image.LANCZOS), (x, 650))
S = S.crop((0, 0, S.width, 890)); S.save(PV / 'real-size-check.png', optimize=True)
print('sheets ->', PV)
