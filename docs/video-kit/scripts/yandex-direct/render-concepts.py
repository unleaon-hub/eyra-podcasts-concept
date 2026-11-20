#!/usr/bin/env python3
"""Render the Yandex Direct concept stage: concepts A–D x experts x 3 sizes (4:3, 1:1, 16:9).
Usage: python3 render-concepts.py [--c A,B] [--e asya,lera] ; output ../../yandex-direct/concepts/<C>/ (DIRECT_OUT overrides)."""
import argparse, asyncio, json, os, shutil, urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get('DIRECT_OUT', HERE.parents[1] / 'yandex-direct' / 'concepts'))
SIZES = [(1440, 1080, '4x3'), (1080, 1080, '1x1'), (1920, 1080, '16x9')]
NAMES = {'A': 'A-solnechnaya-scena', 'B': 'B-cvetnoy-akcent', 'C': 'C-razgovor-v-telegram', 'D': 'D-krupnyy-portret'}
async def main(cs, es):
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable'); args = ['--allow-file-access-from-files', '--no-sandbox']
    res = []
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=chrome, args=args) if chrome else p.chromium.launch(args=args))
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        for c in cs:
            for e in es:
                for w, h, tag in SIZES:
                    await pg.set_viewport_size({'width': w, 'height': h})
                    await pg.goto((HERE / 'direct.html').as_uri() + '?' + urllib.parse.urlencode({'c': c, 'e': e, 'w': w, 'h': h}))
                    await pg.wait_for_selector('body[data-ready]', state='attached'); await pg.wait_for_timeout(150)
                    qa = await pg.evaluate('window.QA'); out = OUT / NAMES[c] / f'{e}-{c}-{tag}-{w}x{h}.jpg'; out.parent.mkdir(parents=True, exist_ok=True)
                    tmp = out.with_suffix('.png'); await pg.screenshot(path=str(tmp)); Image.open(tmp).convert('RGB').save(out, quality=90, optimize=True); tmp.unlink()
                    ok = not errs and qa.get('over', 0) == 0; res.append((out.name, ok, qa))
                    print('OK ' if ok else 'BAD', out.name, 'fs', qa.get('fs'), 'text%', qa.get('text'), 'KB', out.stat().st_size // 1024, *errs); errs.clear()
        await b.close()
    return res
if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('--c', default='A,B,C,D'); a.add_argument('--e', default='asya,lera,mira')
    o = a.parse_args(); asyncio.run(main(o.c.split(','), o.e.split(',')))
