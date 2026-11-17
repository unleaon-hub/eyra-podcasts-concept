#!/usr/bin/env python3
"""EYRA · обложка нового выпуска (или кадр для видео) по id эксперта и короткому названию.

  python3 new-cover.py asya "Как пережить расставание"                  -> asya-<slug>-1920x1080.jpg
  python3 new-cover.py kira "Сахар и усталость" --kind frame            -> кадр для видео (PNG)
  python3 new-cover.py vera "Луна в Раке" --out ~/covers/ep14.jpg

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
EXPERTS = 'asya kira vera lera mira nika eva maya sofia alisa'.split()

def slug(s):
    tr = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sch','','y','','e','yu','ya']))
    s = ''.join(tr.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'episode'

async def render(e, title, kind, out):
    f = 'th' if kind == 'episode' else 'fr'
    url = (HERE / 'scene.html').as_uri() + '?' + urllib.parse.urlencode({'e': e, 'f': f, 't': title})
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome, args=['--allow-file-access-from-files']) if chrome else \
            await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1.5)
        await pg.goto(url); await pg.wait_for_selector('body[data-ready]')
        gap = await pg.evaluate('gap()')
        fit = await pg.evaluate("""(()=>{const t=document.querySelectorAll('.t')[1];const lh=parseFloat(getComputedStyle(t).lineHeight);
            return {lines:Math.round(t.scrollHeight/lh),overflow:t.scrollWidth>t.clientWidth+1}})()""")
        tmp = str(out) + '.png'
        await pg.screenshot(path=tmp); await b.close()
    im = Image.open(tmp).convert('RGB'); os.remove(tmp)
    assert im.size == (1920, 1080), im.size
    if str(out).lower().endswith('.png'): im.save(out)
    else: im.save(out, quality=92, optimize=True)
    warn = [g[0] for g in gap if g[1] > 0]
    if warn: print('⚠ текст задевает эксперта:', warn, '— сократите название')
    if fit['lines'] > 3 or fit['overflow']: print('⚠ название не помещается (строк: %d) — сократите' % fit['lines'])
    if not warn and fit['lines'] <= 3 and not fit['overflow']: print('✓ проверка пройдена')
    print('→', out, '(%.0f КБ)' % (os.path.getsize(out) / 1024))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('expert', choices=EXPERTS); ap.add_argument('title')
    ap.add_argument('--kind', choices=['episode', 'frame'], default='episode')
    ap.add_argument('--out')
    a = ap.parse_args()
    out = a.out or f"{a.expert}-{slug(a.title)}-{'1920x1080.jpg' if a.kind == 'episode' else 'frame-1920x1080.png'}"
    asyncio.run(render(a.expert, a.title, a.kind, os.path.expanduser(out)))
