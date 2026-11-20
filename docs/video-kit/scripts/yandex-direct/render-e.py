#!/usr/bin/env python3
"""Render concept E (benchmark layout). Out: ../../yandex-direct/concepts/E-benchmark/ (override DIRECT_OUT)."""
import os, sys, argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get('DIRECT_OUT', HERE.parent.parent / 'yandex-direct' / 'concepts' / 'E-benchmark')); OUT.mkdir(parents=True, exist_ok=True)
a = argparse.ArgumentParser(); a.add_argument('--e', default='mira,asya,lera,kira,sofia'); a.add_argument('--v', default='1,2,3'); a.add_argument('--f', default='4x3,16x9'); o = a.parse_args()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files'])
    for f in o.f.split(','):
        pg = b.new_page(viewport={'width': 1920 if f == '16x9' else 1440, 'height': 1080})
        for e in o.e.split(','):
            for v in o.v.split(','):
                pg.goto(f'file://{HERE}/benchmark.html?e={e}&v={v}&f={f}'); pg.wait_for_function("document.title==='ready'", timeout=20000)
                fn = OUT / f'E{v}-{e}-{f}.jpg'; pg.locator('#c').screenshot(path=str(fn), type='jpeg', quality=92); print(fn.name)
    b.close()
