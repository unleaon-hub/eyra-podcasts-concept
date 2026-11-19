#!/usr/bin/env python3
"""Screenshot the Threads mocks at phone width (390 px, 2x): previews/threads-profile-mock.png and threads-thread-mock-<id>.png.
Usage: python3 shot-mock.py [expert ...]   (default thread: asya). Output: ../../threads/previews (TH_OUT overrides ../../threads)."""
import asyncio, os, shutil, sys
from pathlib import Path
from playwright.async_api import async_playwright
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get('TH_OUT', HERE.parents[1] / 'threads')) / 'previews'
async def main(ex):
    OUT.mkdir(parents=True, exist_ok=True); chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    args = ['--allow-file-access-from-files', '--no-sandbox']
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=chrome, args=args) if chrome else p.chromium.launch(args=args))
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        for q, name in [('v=profile', 'threads-profile-mock.png')] + [(f'v=thread&e={e}', f'threads-thread-mock-{e}.png') for e in ex]:
            await pg.goto((HERE / 'mock.html').as_uri() + '?' + q); await pg.wait_for_selector('body[data-ready]', state='attached'); await pg.wait_for_timeout(300)
            bad = await pg.evaluate('[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src)')
            await pg.screenshot(path=str(OUT / name), full_page=True); print('OK ' if not (bad or errs) else 'BAD', name, *bad, *errs); errs.clear()
        await b.close()
asyncio.run(main(sys.argv[1:] or ['asya']))
