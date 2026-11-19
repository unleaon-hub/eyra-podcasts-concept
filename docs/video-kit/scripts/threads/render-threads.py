#!/usr/bin/env python3
"""Render the EYRA Threads set in the Instagram v5 style (same template ig.html).
  posts/        10 x scene + question, 1080x1350 (4:5) - first post of each thread
  quotes/       10 x quote card on a still-life plate, 1080x1350
  link-preview/ 11 x og:image proposal, 1200x630 (home + 10 experts) - set on the SITE, not in Threads
Usage: python3 render-threads.py [posts|quotes|og ...]   (default: all)
Output: ../../threads/ (override with TH_OUT=/path)."""
import asyncio, csv, importlib.util, json, os, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
IG = next(p for p in (HERE.parent / 'instagram', HERE.parent / 'ig') if (p / 'ig.html').exists())
OUT = Path(os.environ.get('TH_OUT', HERE.parents[1] / 'threads'))
spec = importlib.util.spec_from_file_location('newpost', IG / 'new-post.py'); NP = importlib.util.module_from_spec(spec); spec.loader.exec_module(NP)
D = json.load(open(HERE / 'threads.json', encoding='utf-8'))
ORDER = ['asya', 'kira', 'vera', 'lera', 'mira', 'nika', 'eva', 'maya', 'sofia', 'alisa']
COVER = {r[0]: (r[2].replace('&nbsp;', '\u00a0'), r[3]) for r in csv.reader(open(IG / 'carousels.tsv', encoding='utf-8'), delimiter='\t') if len(r) > 3 and r[1] == 'carcover'}
q = lambda t: t + '?' if re.match(r'^(Как|Что|С\s+чего|Куда|Где|Когда)\b', t) else t

def jobs(parts):
    J = []
    if 'posts' in parts:
        J += [{'e': e, 'kind': 'post', 't': q(COVER[e][0]), 's': COVER[e][1] + ' — в ветке ниже', 'out': str(OUT / 'posts' / f'{e}-post-1080x1350.jpg')} for e in ORDER]
    if 'quotes' in parts:
        J += [{'e': e, 'kind': 'quote', 't': D['experts'][e]['quote'], 'out': str(OUT / 'quotes' / f'{e}-quote-1080x1350.jpg')} for e in ORDER]
    if 'og' in parts:
        if not (IG / 'bg-og-home.jpg').exists(): subprocess.run([sys.executable, str(IG / 'mk-og.py')], check=True)
        J += [{'e': 'asya', 'kind': 'og-home', 'out': str(OUT / 'link-preview' / 'og-home-1200x630.jpg')}]
        J += [{'e': e, 'kind': 'og', 'out': str(OUT / 'link-preview' / f'og-{e}-1200x630.jpg')} for e in ORDER]
    return J

if __name__ == '__main__':
    parts = sys.argv[1:] or ['posts', 'quotes', 'og']
    res = asyncio.run(NP.render_many(jobs(parts)))
    bad = [r['out'] for r in res if not r['ok']]
    print(f'{len(res) - len(bad)}/{len(res)} OK ->', OUT)
    sys.exit(1 if bad else 0)
