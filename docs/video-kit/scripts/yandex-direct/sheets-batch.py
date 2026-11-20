# Preview sheets for the Yandex Direct batch -> yandex-direct/previews/batch-*.jpg
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
H = Path(__file__).resolve().parent; C = H.parent.parent / 'yandex-direct' / 'creatives'; P = H.parent.parent / 'yandex-direct' / 'previews'
P.mkdir(exist_ok=True)
B = json.loads(open(H/'batch/heads.js').read().split('window.BATCH=',1)[1].strip().rstrip(';'))
IDS = 'kira asya eva sofia mira lera vera nika maya alisa'.split()
NAMES = dict(kira='Кира', asya='Ася', eva='Ева', sofia='София', mira='Мира', lera='Лера', vera='Вера', nika='Ника', maya='Майя', alisa='Алиса')
f = lambda s, w='Regular': ImageFont.truetype(str(H/f'fonts/Pretendard-{w}.otf'), s)
def file(e, n, fm): s = B[e][n-1][0]; return C/e/f'{n}-{s}-{fm}.jpg'
def thumb(p, h): im = Image.open(p).convert('RGB'); return im.resize((round(im.width*h/im.height), h), Image.LANCZOS)
BG = (244, 242, 238); INK = (23, 25, 29)

# 1 overview: all 50 in 4:3
tw, th, g, lw = 384, 288, 12, 120
im = Image.new('RGB', (lw + 5*(tw+g) + g, 90 + 10*(th+g) + g), BG); d = ImageDraw.Draw(im)
d.text((g, 26), 'EYRA × Яндекс Директ · партия F2 · 50 креативов (4:3, 1440×1080) · «1» = главный хук из банка', font=f(30, 'Medium'), fill=INK)
for r, e in enumerate(IDS):
    y = 90 + r*(th+g); d.text((g, y + th//2 - 14), NAMES[e], font=f(28, 'Medium'), fill=INK)
    for c in range(5):
        im.paste(thumb(file(e, c+1, '4x3'), th), (lw + c*(tw+g), y))
        d.text((lw + c*(tw+g) + 8, y + th - 26), f'{c+1}' + (' главный' if c == 0 else '') + ' · '  + f'{B[e][c][2].upper()}', font=f(18, 'Medium'), fill=(255, 255, 255))
im.save(P/'batch-01-overview-4x3.jpg', quality=88)

# 2 per expert: 5 creatives × 4 formats
for e in IDS:
    h = 300; cols = ['4x3', '16x9', '1x1', '3x4']; ws = [400, 533, 300, 225]
    W = 70 + sum(ws) + 5*g; im = Image.new('RGB', (W, 80 + 5*(h+g) + g), BG); d = ImageDraw.Draw(im)
    d.text((g, 22), f'{NAMES[e]} · 5 креативов × 4 формата (4:3 · 16:9 · 1:1 · 3:4)', font=f(30, 'Medium'), fill=INK)
    for n in range(1, 6):
        y = 80 + (n-1)*(h+g); x = 70; d.text((g+10, y + h//2 - 16), str(n), font=f(30, 'Medium'), fill=INK)
        for fm, w in zip(cols, ws):
            im.paste(thumb(file(e, n, fm), h), (x, y)); x += w + g
    im.save(P/f'batch-expert-{e}.jpg', quality=86)

# 3 formats sheet for one creative (Мира 1 (главный)) at larger size
e, n = 'mira', 1; h = 540
ts = [thumb(file(e, n, fm), h) for fm in ['4x3', '16x9', '1x1', '3x4']]
im = Image.new('RGB', (sum(t.width for t in ts) + 5*g, h + 110), BG); d = ImageDraw.Draw(im); x = g
d.text((g, 20), 'Мира 1 (главный) «Что скажут ваши числа» — 4 формата пересобраны (не автокроп): 4:3 1440×1080 · 16:9 1920×1080 · 1:1 1080×1080 · 3:4 1080×1440', font=f(24, 'Medium'), fill=INK)
for t in ts: im.paste(t, (x, 70)); x += t.width + g
im.save(P/'batch-02-formats-mira-1.jpg', quality=88)

# 4 before -> after (approved moderation creative / benchmark vs final)
ref = H.parent.parent/'yandex-direct'/'reference'/'ref-6-mira-lilac.png'
a = thumb(ref, 540); b = thumb(file('mira', 1, '4x3'), 540); c2 = thumb(file('mira', 3, '4x3'), 540)
im = Image.new('RGB', (a.width + b.width + c2.width + 4*g, 540 + 110), BG); d = ImageDraw.Draw(im)
d.text((g, 20), 'До → после: эталон (одобренный креатив Миры) → партия F2 (креативы 1 и 3: другая сцена и кадр)', font=f(26, 'Medium'), fill=INK)
x = g
for t in (a, b, c2): im.paste(t, (x, 70)); x += t.width + g
im.save(P/'batch-03-before-after-mira.jpg', quality=88)

# 5 real size: 320×240 (4:3) and 300×300 (1:1), all 10 ★1 + one extra
im = Image.new('RGB', (5*(320+g) + g, 60 + 2*(240+g) + 2*(300+g) + g), BG); d = ImageDraw.Draw(im)
d.text((g, 16), 'Реальный размер: 320×240 (4:3) и 300×300 (1:1), без увеличения', font=f(24, 'Medium'), fill=INK)
for i, e in enumerate(IDS):
    n = 1 + (i % 5)
    t = Image.open(file(e, n, '4x3')).convert('RGB').resize((320, 240), Image.LANCZOS); im.paste(t, (g + (i % 5)*(320+g), 60 + (i//5)*(240+g)))
    t = Image.open(file(e, n, '1x1')).convert('RGB').resize((300, 300), Image.LANCZOS); im.paste(t, (g + (i % 5)*(320+g), 60 + 2*(240+g) + (i//5)*(300+g)))
im.save(P/'batch-04-real-size.png')

# 6 faces: face crop of every creative (4:3) per expert, to check consistency across scenes a/b and zoom
geo = json.loads(open(H/'batch/geo.js').read().split('window.GEO=',1)[1].strip().rstrip(';'))
rep = json.loads(open(H/'batch/report.json').read())
s = 150; im = Image.new('RGB', (110 + 5*(s+6), 60 + 10*(s+6)), BG); d = ImageDraw.Draw(im)
d.text((g, 16), 'Лица: все 50 креативов (4:3), один эксперт = одна строка', font=f(24, 'Medium'), fill=INK)
for r, e in enumerate(IDS):
    d.text((g, 60 + r*(s+6) + s//2 - 12), NAMES[e], font=f(22, 'Medium'), fill=INK)
    for n in range(1, 6):
        key = f'{e}/{n}-{B[e][n-1][0]}-4x3'; info = rep[key]; G = geo[f'{e}-{B[e][n-1][2]}']
        z, off = info['z'], info['off']; sy = info.get('sy', 0)
        cx = (G['hcx'] - off)*z; cy = (G['hcy'] - sy)*z; R = 150*z
        t = Image.open(file(e, n, '4x3')).convert('RGB').crop((int(cx-R), int(cy-R), int(cx+R), int(cy+R))).resize((s, s), Image.LANCZOS)
        im.paste(t, (110 + (n-1)*(s+6), 60 + r*(s+6)))
im.save(P/'batch-05-faces.jpg', quality=88)
print('sheets ok')
