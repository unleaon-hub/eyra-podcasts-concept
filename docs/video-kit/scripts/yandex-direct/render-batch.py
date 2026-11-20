#!/usr/bin/env python3
"""Render the Yandex Direct batch -> ../../yandex-direct/creatives/<id>/<n>-<slug>-{4x3,1x1,16x9,3x4}.jpg + batch/report.json
   --e ids (default all 10)  --n 1,2,3,4,5  --f 4x3,16x9,1x1,3x4"""
import os, argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent; OUT = Path(os.environ.get('DIRECT_OUT', HERE.parent.parent / 'yandex-direct' / 'creatives'))
a = argparse.ArgumentParser(); a.add_argument('--e', default='kira,asya,eva,sofia,mira,lera,vera,nika,maya,alisa'); a.add_argument('--n', default='1,2,3,4,5'); a.add_argument('--f', default='4x3,16x9,1x1,3x4'); o = a.parse_args()
SZ = {'4x3': (1440, 1080), '16x9': (1920, 1080), '1x1': (1080, 1080), '3x4': (1080, 1440)}
RJ = HERE / 'batch' / 'report.json'; REP = json.loads(RJ.read_text()) if RJ.exists() else {}
B = json.loads((HERE / 'batch' / 'heads.js').read_text().split('window.BATCH=', 1)[1].strip().rstrip(';'))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files'])
    for f in o.f.split(','):
        W, H = SZ[f]; pg = b.new_page(viewport={'width': W, 'height': H})
        for e in o.e.split(','):
            (OUT / e).mkdir(parents=True, exist_ok=True)
            for n in map(int, o.n.split(',')):
                pg.goto(f'file://{HERE}/batch.html?e={e}&n={n}&f={f}'); pg.wait_for_function("document.title==='ready'", timeout=60000)
                slug = B[e][n - 1][0]; fn = OUT / e / f'{n}-{slug}-{f}.jpg'
                pg.locator('#c').screenshot(path=str(fn), type='jpeg', quality=90)
                info = pg.evaluate('window.INFO'); info['kb'] = fn.stat().st_size // 1024; REP[f'{e}/{n}-{slug}-{f}'] = info
                flag = '' if info['faceOK'] and info['end'] < info['hair'] - 20 and info['kb'] < 4000 else '  <-- CHECK'
                print(f'{e}/{n}-{slug}-{f}', json.dumps(info, ensure_ascii=False), flag, flush=True)
        pg.close()
    b.close()
RJ.write_text(json.dumps(REP, ensure_ascii=False, indent=0))
