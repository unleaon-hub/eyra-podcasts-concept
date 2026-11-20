#!/usr/bin/env python3
"""Render concept F -> ../../yandex-direct/concepts/F-depth/F-<id>-4x3.jpg (1440x1080)."""
import os, argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get('DIRECT_OUT', HERE.parent.parent / 'yandex-direct' / 'concepts' / 'F-depth')); OUT.mkdir(parents=True, exist_ok=True)
a = argparse.ArgumentParser(); a.add_argument('--e', default='kira,asya,eva,mira,sofia'); o = a.parse_args()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width': 1440, 'height': 1080})
    for e in o.e.split(','):
        pg.goto(f'file://{HERE}/depth.html?e={e}'); pg.wait_for_function("document.title==='ready'", timeout=30000)
        fn = OUT / f'F-{e}-4x3.jpg'; pg.locator('#c').screenshot(path=str(fn), type='jpeg', quality=92); print(fn.name, json.dumps(pg.evaluate('window.INFO')))
    b.close()
