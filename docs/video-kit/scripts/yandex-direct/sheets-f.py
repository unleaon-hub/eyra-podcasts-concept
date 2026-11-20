#!/usr/bin/env python3
"""Concept F sheets -> ../../yandex-direct/concepts/F-depth/previews/
 F-main.jpg       row 1: benchmark | Mira E2 | Mira F ; row 2: five experts F
 F-proof-mira.jpg benchmark vs Mira F full size + split-tone glyph zoom of both
 F-faces.jpg      face check: kit scene (left) vs F scene (right) for each expert
 F-real-size.png  320x240"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; K = HERE.parent.parent / 'yandex-direct'; D = K / 'concepts' / 'F-depth'; P = D / 'previews'; P.mkdir(exist_ok=True)
EX = ['kira', 'asya', 'eva', 'mira', 'sofia']; NM = dict(mira='Мира', asya='Ася', eva='Ева', kira='Кира', sofia='София')
F = ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Regular.otf'), 26); FB = ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Medium.otf'), 30)
BG = (246, 244, 241); ref = Image.open(K / 'reference' / 'ref-6-mira-lilac.png').convert('RGB').resize((1440, 1080), Image.LANCZOS)
def im(p): return Image.open(p).convert('RGB')
def grid(items, cols, tw, th, title, gap=24):
    rows = (len(items) + cols - 1) // cols; s = Image.new('RGB', (cols * tw + (cols + 1) * gap, 90 + rows * (th + 44 + gap) + gap), BG); d = ImageDraw.Draw(s)
    d.text((gap, 30), title, font=FB, fill=(23, 25, 29))
    for i, (x, c) in enumerate(items):
        X = gap + (i % cols) * (tw + gap); Y = 90 + (i // cols) * (th + 44 + gap); s.paste(x.resize((tw, th), Image.LANCZOS), (X, Y)); d.text((X, Y + th + 8), c, font=F, fill=(70, 72, 78))
    return s
a = grid([(ref, 'Эталон'), (im(K / 'concepts/E-benchmark/E2-mira-4x3.jpg'), 'Мира · E2 (прошлый шаг)'), (im(D / 'F-mira-4x3.jpg'), 'Мира · F «Глубина»')], 3, 853, 640, 'Концепт F · две зоны + текст меняет цвет на границе · 4:3 1440×1080 · ЧЕРНОВИК')
b = grid([(im(D / f'F-{e}-4x3.jpg'), f'{NM[e]} · F') for e in EX], 5, 512, 384, 'Пять экспертов · сильный заход из банка заголовков')
s = Image.new('RGB', (max(a.width, b.width), a.height + b.height), BG); s.paste(a, ((s.width - a.width) // 2, 0)); s.paste(b, ((s.width - b.width) // 2, a.height)); s.save(P / 'F-main.jpg', quality=90)
mf = im(D / 'F-mira-4x3.jpg')
items = [(ref, 'Эталон'), (mf, 'Мира · F'), (ref.crop((380, 230, 760, 540)), 'Эталон: «плаНЫ» — буквы белеют ровно по краю тёмной стены'), (mf.crop((420, 260, 800, 570)), 'F: та же логика, маска по реальным тёмным пикселям фона')]
grid(items, 2, 960, 720, 'Сверка с эталоном').save(P / 'F-proof-mira.jpg', quality=90)
# faces: kit scene vs F scene, crop around the head
W = HERE.parent / 'template' / 'work'; items = []
for e in EX:
    import numpy as np
    m = np.asarray(Image.open(HERE / 'scenes-f' / f'{e}-16x9-mask.png')) > 100; xs = np.nonzero(m[:300].any(0))[0]; cx = int(xs.mean())
    box = (cx - 260, 0, cx + 260, 520)
    old = im(W / f'{e}-16x9-up.jpg'); mo = np.asarray(Image.open(W / f'{e}-16x9-mask.png')) > 100; ox = int(np.nonzero(mo[:300].any(0))[0].mean())
    items += [(old.crop((ox - 260, 0, ox + 260, 520)), f'{NM[e]} · сцена кита'), (im(HERE / 'scenes-f' / f'{e}-16x9-up.jpg').crop(box), f'{NM[e]} · сцена F')]
grid(items, 4, 360, 360, 'Проверка лиц: слева сцена кита, справа отредактированная сцена F').save(P / 'F-faces.jpg', quality=88)
items = [(ref, 'эталон'), (im(K / 'concepts/E-benchmark/E2-mira-4x3.jpg'), 'Мира E2')] + [(im(D / f'F-{e}-4x3.jpg'), f'{NM[e]} F') for e in EX]
s = Image.new('RGB', (4 * 340 + 20, 2 * 290 + 70), BG); d = ImageDraw.Draw(s); d.text((20, 14), 'Реальный размер 320×240', font=F, fill=(23, 25, 29)); f2 = ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Regular.otf'), 18)
for i, (x, c) in enumerate(items):
    X = 20 + (i % 4) * 340; Y = 60 + (i // 4) * 290; s.paste(x.resize((320, 240), Image.LANCZOS), (X, Y)); d.text((X, Y + 246), c, font=f2, fill=(70, 72, 78))
s.save(P / 'F-real-size.png')
