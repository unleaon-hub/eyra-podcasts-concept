#!/usr/bin/env python3
"""EYRA · Pinterest: пин 1000×1500 в светлом стиле.

  python3 new-pin.py sofia "Копить на дом вместе" "как договориться о совместной цели в паре или семье"
  python3 new-pin.py maya "Отдых и привычки" --kind board          -> обложка доски
  python3 new-pin.py eva "Когда среда не работает" --kind alt-b     -> запасной вариант «рамка»

Заголовок — часть названия статьи до двоеточия, подстрока — после (необязательно).
Пишет <expert>-<slug>-pin-1000x1500.jpg в текущую папку (или --out). Печатает QA: размер шрифта и зазор до головы.
Нужно: Python 3, pip install playwright pillow; Chrome в системе или `playwright install chromium`.
"""
import argparse, asyncio, json, re, shutil, sys, urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
EXPERTS = 'asya kira vera lera mira nika eva maya sofia alisa'.split()
HEADS = json.load(open(HERE / 'pbg.json'))
BOARD_FS = 76  # одна высота темы на всех обложках досок

def slug(s):
    tr = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sch','','y','','e','yu','ya']))
    s = ''.join(tr.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'pin'

def query(e, title, sub='', kind='pin'):
    m = {'pin': 'a', 'board': 'c', 'alt-b': 'b'}[kind]
    q = {'e': e, 'm': m, 't': title, 'head': HEADS['b' if m == 'c' else 'a'][e]['head']}
    if sub: q['s'] = sub
    if m == 'c': q['fs'] = BOARD_FS
    return (HERE / 'pin.html').as_uri() + '?' + urllib.parse.urlencode(q)

async def render_many(jobs):
    """jobs: list of (expert, title, sub, kind, out_path). Returns list of qa dicts."""
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    args = ['--allow-file-access-from-files', '--no-sandbox']
    res = []
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=chrome, args=args) if chrome else p.chromium.launch(args=args))
        pg = await b.new_page(viewport={'width': 1000, 'height': 1500})
        errs = []; pg.on('pageerror', lambda x: errs.append(str(x)))
        for e, title, sub, kind, out in jobs:
            await pg.goto(query(e, title, sub, kind)); await pg.wait_for_selector('body[data-ready]', state='attached')
            qa = await pg.evaluate('qa'); png = Path(out).with_suffix('.tmp.png')
            await pg.screenshot(path=str(png))
            Image.open(png).convert('RGB').save(out, quality=94, subsampling=0); png.unlink()
            qa.update(out=str(out), gap=round(qa['limit'] - qa['bottom']), ok=qa['bottom'] <= qa['limit'] and not errs and (kind != 'board' or (qa.get('w', 0) <= 820 and qa.get('lines') == 1)))
            res.append(qa); print(('OK ' if qa['ok'] else 'BAD'), Path(out).name, 'fs', qa['fs'], 'gap', qa['gap'], *errs)
        await b.close()
    return res

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('expert', choices=EXPERTS); a.add_argument('title'); a.add_argument('sub', nargs='?', default='')
    a.add_argument('--kind', choices=['pin', 'board', 'alt-b'], default='pin'); a.add_argument('--out')
    x = a.parse_args()
    suf = {'pin': 'pin', 'board': 'board-cover', 'alt-b': 'pin-B'}[x.kind]
    out = x.out or f"{x.expert}-{slug(x.title)}-{suf}-1000x1500.jpg"
    r = asyncio.run(render_many([(x.expert, x.title, x.sub, x.kind, out)]))
    sys.exit(0 if r[0]['ok'] else 1)

if __name__ == '__main__':
    main()
