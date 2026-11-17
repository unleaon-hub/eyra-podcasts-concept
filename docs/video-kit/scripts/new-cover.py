#!/usr/bin/env python3
"""EYRA · обложка нового выпуска (или кадр для видео) по id эксперта и короткому названию.

  python3 new-cover.py asya "Как пережить расставание"                  -> asya-<slug>-1920x1080.jpg
  python3 new-cover.py kira "Сахар и усталость" --kind frame            -> кадр для видео (PNG)
  python3 new-cover.py vera "Луна в Раке" --out ~/covers/ep14.jpg
  python3 new-cover.py eva "Как найти друзей" --kind vertical          -> обложка Ролика Дзена 1080×1920 (JPG)
  python3 new-cover.py eva "Как найти друзей" --kind vertical-frame    -> кадр для make-vertical-teaser.sh (PNG)

Эксперты: asya kira vera lera mira nika eva maya sofia alisa
Нужно: Python 3, pip install playwright pillow, затем `playwright install chromium`
(или установленный Google Chrome). Название — 2–3 строки, лучше до ~32 знаков.
Скрипт сам проверит, что текст не заходит на эксперта и не вылезает за колонку.
"""
import argparse, asyncio, os, re, shutil, sys, urllib.parse
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent / 'template'
VHERE = Path(__file__).resolve().parent / 'template-vertical'
EXPERTS = 'asya kira vera lera mira nika eva maya sofia alisa'.split()

def slug(s):
    tr = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sch','','y','','e','yu','ya']))
    s = ''.join(tr.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'episode'

async def render(e, title, kind, out):
    vert = kind.startswith('vertical')
    if vert:
        url = (VHERE / 'vert.html').as_uri() + '?' + urllib.parse.urlencode({'e': e, 'f': 'f' if kind == 'vertical-frame' else 'c', 't': title})
        size, vp, dpr = (1080, 1920), {'width': 1080, 'height': 1920}, 1
    else:
        f = 'th' if kind == 'episode' else 'fr'
        url = (HERE / 'scene.html').as_uri() + '?' + urllib.parse.urlencode({'e': e, 'f': f, 't': title})
        size, vp, dpr = (1920, 1080), {'width': 1280, 'height': 720}, 1.5
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome, args=['--allow-file-access-from-files']) if chrome else \
            await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await b.new_page(viewport=vp, device_scale_factor=dpr)
        await pg.goto(url); await pg.wait_for_selector('body[data-ready]', state='attached')
        if vert:
            qa = await pg.evaluate('qa')
            warn = ['эксперт'] if qa['bottom'] > qa['head'] - 24 else []
            fit = {'lines': qa['lines'], 'overflow': qa['fs'] < 96}
        else:
            gap = await pg.evaluate('gap()')
            fit = await pg.evaluate("""(()=>{const t=document.querySelectorAll('.t')[1];const lh=parseFloat(getComputedStyle(t).lineHeight);
                return {lines:Math.round(t.scrollHeight/lh),overflow:t.scrollWidth>t.clientWidth+1}})()""")
            warn = [g[0] for g in gap if g[1] > 0]
        lay = await pg.evaluate('window.layout || null') if kind in ('frame', 'vertical-frame') else None
        tmp = str(out) + '.png'
        await pg.screenshot(path=tmp); await b.close()
    im = Image.open(tmp).convert('RGB'); os.remove(tmp)
    assert im.size == size, im.size
    if str(out).lower().endswith('.png'): im.save(out)
    else: im.save(out, quality=92, optimize=True)
    if lay:  # sidecar with waveform/progress position for make-episode-video.sh / make-vertical-teaser.sh
        k = 1 if vert else 1.5
        w = [round(v * k) for v in lay['wave']]; t = [round(v * k) for v in lay['track']]; w[2] -= w[2] % 2; w[3] -= w[3] % 2
        side = os.path.splitext(str(out))[0] + '.layout'
        open(side, 'w').write(' '.join(str(v) for v in w + t) + '\n')
        print('→', side, '(положение волны для видео)')
    if warn: print('⚠ текст задевает эксперта:', warn, '— сократите название')
    if fit['lines'] > 3 or fit['overflow']: print('⚠ название не помещается крупным кеглем (строк: %d) — сократите' % fit['lines'])
    if not warn and fit['lines'] <= 3 and not fit['overflow']: print('✓ проверка пройдена')
    print('→', out, '(%.0f КБ)' % (os.path.getsize(out) / 1024))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('expert', choices=EXPERTS); ap.add_argument('title')
    ap.add_argument('--kind', choices=['episode', 'frame', 'vertical', 'vertical-frame'], default='episode')
    ap.add_argument('--out')
    a = ap.parse_args()
    suf = {'episode': '1920x1080.jpg', 'frame': 'frame-1920x1080.png', 'vertical': 'vertical-1080x1920.jpg', 'vertical-frame': 'vertical-frame-1080x1920.png'}[a.kind]
    out = a.out or f"{a.expert}-{slug(a.title)}-{suf}"
    asyncio.run(render(a.expert, a.title, a.kind, os.path.expanduser(out)))
