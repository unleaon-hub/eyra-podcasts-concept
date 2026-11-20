#!/usr/bin/env python3
"""Render concept F (--sd scenes-f2 --tag F2 for F2) -> ../../yandex-direct/concepts/F-depth/F-<id>-4x3.jpg (1440x1080)."""
import os, argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
a = argparse.ArgumentParser(); a.add_argument('--e', default='kira,asya,eva,mira,sofia'); a.add_argument('--sd', default='scenes-f'); a.add_argument('--tag', default='F'); o = a.parse_args()
OUT = Path(os.environ.get('DIRECT_OUT', HERE.parent.parent / 'yandex-direct' / 'concepts' / ('F-depth' if o.tag == 'F' else 'F2-darker'))); OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width': 1440, 'height': 1080})
    for e in o.e.split(','):
        pg.goto(f'file://{HERE}/depth.html?e={e}&sd={o.sd}'); pg.wait_for_function("document.title==='ready'", timeout=30000)
        fn = OUT / f'{o.tag}-{e}-4x3.jpg'; pg.locator('#c').screenshot(path=str(fn), type='jpeg', quality=92); print(fn.name, json.dumps(pg.evaluate('window.INFO')))
    b.close()
