#!/usr/bin/env python3
"""Concept E preview sheets -> ../../yandex-direct/concepts/E-benchmark/previews/
 1 E-main.jpg          row 1: benchmark | Mira E1 | E2 | E3 ; row 2: five experts in E2
 2 E-proof-mira.jpg    benchmark vs Mira E1 at full size + type overlay (benchmark red, E1 blue)
 3 E-crops.jpg         what Direct's auto-crop of the 4:3 does: 16:9 centre, 1:1 centre, 1:1 on the face
 4 E-real-size.png     320x240 (real size in the feed) for all five E2 + Mira E1/E3
 5 E-all.jpg           every file (E1/E2/E3 x five, 4:3) + the dedicated 16:9 renders"""
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; D = HERE.parent.parent / 'yandex-direct' / 'concepts' / 'E-benchmark'; P = D / 'previews'; P.mkdir(exist_ok=True)
REF = HERE.parent.parent / 'yandex-direct' / 'reference' / 'ref-6-mira-lilac.png'
EX = ['mira', 'asya', 'lera', 'kira', 'sofia']; NM = dict(mira='Мира', asya='Ася', lera='Лера', kira='Кира', sofia='София')
F = ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Regular.otf'), 26); FB = ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Medium.otf'), 30)
ref = Image.open(REF).convert('RGB').resize((1440, 1080), Image.LANCZOS)
def im(n): return Image.open(D / n).convert('RGB')
def grid(items, cols, tw, th, title, gap=24, lab=44):
    rows = (len(items) + cols - 1) // cols; W = cols * tw + (cols + 1) * gap; H = 90 + rows * (th + lab + gap) + gap
    s = Image.new('RGB', (W, H), (246, 244, 241)); d = ImageDraw.Draw(s); d.text((gap, 30), title, font=FB, fill=(23, 25, 29))
    for i, (img, cap) in enumerate(items):
        if img is None: continue
        x = gap + (i % cols) * (tw + gap); y = 90 + (i // cols) * (th + lab + gap)
        s.paste(img.resize((tw, th), Image.LANCZOS), (x, y)); d.text((x, y + th + 8), cap, font=F, fill=(70, 72, 78))
    return s
# 1 main
row1 = [(ref, 'Эталон (одобренный креатив)'), (im('E1-mira-4x3.jpg'), 'Мира · E1 точная копия системы'), (im('E2-mira-4x3.jpg'), 'Мира · E2 + EYRA + «Без банковской карты»'), (im('E3-mira-4x3.jpg'), 'Мира · E3 = E2, плашка в акценте')]
row2 = [(im(f'E2-{e}-4x3.jpg'), f'{NM[e]} · E2') for e in EX] 
a = grid(row1, 4, 640, 480, 'Концепт E · система эталона · 4:3 1440×1080 · ЧЕРНОВИК'); b = grid(row2, 5, 512, 384, 'Пять экспертов · вариант E2')
s = Image.new('RGB', (max(a.width, b.width), a.height + b.height), (246, 244, 241)); s.paste(a, (0, 0)); s.paste(b, ((s.width - b.width) // 2, a.height)); s.save(P / 'E-main.jpg', quality=90)
# 2 proof + overlay of dark type pixels
e1 = im('E1-mira-4x3.jpg')
def ink(x): a = np.asarray(x.crop((0, 100, 700, 960)).convert('L')).astype(int); return a < 90
r, e = ink(ref), ink(e1); ov = np.full(r.shape + (3,), 255, np.uint8); ov[r] = (225, 60, 60); ov[e] = (50, 90, 220); ov[r & e] = (30, 30, 30)
iou = (r & e).sum() / (r | e).sum()
pr = Image.new('RGB', (2880 + 700 + 80, 1080 + 110), (246, 244, 241)); d = ImageDraw.Draw(pr)
pr.paste(ref, (20, 90)); pr.paste(e1, (1480, 90)); pr.paste(Image.fromarray(ov), (2940, 190))
d.text((20, 30), 'Эталон', font=FB, fill=(23, 25, 29)); d.text((1480, 30), 'Мира · E1 (наш шаблон)', font=FB, fill=(23, 25, 29))
d.text((2940, 30), f'Наложение текста: красный — эталон, синий — E1, чёрный — совпало', font=F, fill=(23, 25, 29)); d.text((2940, 70), f'IoU тёмных пикселей зоны текста: {iou:.2f}', font=F, fill=(23, 25, 29))
pr.save(P / 'E-proof-mira.jpg', quality=90); print('overlay IoU', round(iou, 3))
# 3 crops: Direct smart-crops the 4:3 if no dedicated file is uploaded
def mark(img, box):
    x = img.copy(); dk = Image.new('RGB', x.size, (0, 0, 0)); m = Image.new('L', x.size, 150); ImageDraw.Draw(m).rectangle(box, fill=0)
    x.paste(dk, (0, 0), m); ImageDraw.Draw(x).rectangle(box, outline=(255, 80, 60), width=6); return x
items = []
for n in ['E2-mira-4x3.jpg', 'E2-asya-4x3.jpg', 'E2-sofia-4x3.jpg']:
    x = im(n); items += [(mark(x, (0, 135, 1439, 944)), f'{n[:-8]} · 16:9 по центру'), (mark(x, (180, 0, 1259, 1079)), '1:1 по центру'), (mark(x, (360, 0, 1439, 1079)), '1:1 на лицо')]
grid(items, 3, 600, 450, 'Автокроп 4:3 в Директе: 16:9 — всё важное остаётся (кроме EYRA); 1:1 — текст режется → нужен отдельный 1:1').save(P / 'E-crops.jpg', quality=88)
# 4 real size
items = [(im(f'E2-{e}-4x3.jpg'), f'{NM[e]} E2') for e in EX] + [(im('E1-mira-4x3.jpg'), 'Мира E1'), (im('E3-mira-4x3.jpg'), 'Мира E3'), (ref.copy(), 'эталон')]
s = Image.new('RGB', (4 * 340 + 20, 2 * 290 + 70), (246, 244, 241)); d = ImageDraw.Draw(s); d.text((20, 14), 'Реальный размер 320×240', font=F, fill=(23, 25, 29))
for i, (x, c) in enumerate(items):
    X = 20 + (i % 4) * 340; Y = 60 + (i // 4) * 290; s.paste(x.resize((320, 240), Image.LANCZOS), (X, Y)); d.text((X, Y + 246), c, font=ImageFont.truetype(str(HERE / 'fonts' / 'Pretendard-Regular.otf'), 18), fill=(70, 72, 78))
s.save(P / 'E-real-size.png')
# 5 all
items = [(im(f'E{v}-{e}-4x3.jpg'), f'E{v} · {NM[e]} · 4:3') for e in EX for v in (1, 2, 3)]
grid(items, 3, 480, 360, 'Все файлы концепта E · 4:3').save(P / 'E-all-4x3.jpg', quality=86)
items = [(im(f'E2-{e}-16x9.jpg'), f'E2 · {NM[e]} · отдельный 16:9 1920×1080') for e in EX]
grid(items, 3, 640, 360, 'Отдельные 16:9 (тот же шаблон, сцена шире)').save(P / 'E-16x9.jpg', quality=86)
