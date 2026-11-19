#!/usr/bin/env python3
"""EYRA · Instagram v2: пересобрать весь набор в ../../instagram/
  pinned/ (3 закреплённых), grid/ (12 постов ленты), carousel/<id>/ (10 каруселей из carousels.tsv),
  stories/ (+ stories/experts/), highlights/, reels/covers, reels/frames (+ .layout), reels/end, previews/stories-guides/.
  python3 render-all.py            # всё
  python3 render-all.py grid pinned   # только части: pinned grid carousel stories highlights reels
"""
import asyncio, importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
np_ = load('np', 'new-post.py'); nc = load('nc', 'new-carousel.py')
OUT = HERE.parent.parent / 'instagram'; S = json.load(open(HERE / 'set.json', encoding='utf-8')); CAR = nc.read_tsv(HERE / 'carousels.tsv')
SX = {}
for line in open(HERE / 'sdata.js', encoding='utf-8'):
    if ':{name:' in line:
        e = line.split(':')[0].strip(); SX[e] = line.split("thumb:'")[1].split("'")[0].replace('&nbsp;', ' ')
PARTS = set(sys.argv[1:]) or {'pinned', 'grid', 'carousel', 'stories', 'highlights', 'reels'}
jobs = []
if 'pinned' in PARTS:
    for i, j in enumerate(S['pinned'], 1):
        jobs.append(dict(j, out=OUT / 'pinned' / f"{i}-{j['kind']}-1080x1350.jpg"))
if 'grid' in PARTS:
    for i, j in enumerate(S['grid'], 1):
        if j['kind'] == 'carousel':
            c = CAR[j['e']][0]; jj = {'e': j['e'], 'kind': 'carcover', 't': c['t'], 'p': c['b'], 'pg': f"1 / {len(CAR[j['e']])}"}
        else:
            jj = {k: v for k, v in j.items() if k != 'note'}
        jobs.append(dict(jj, out=OUT / 'grid' / f"{i:02d}-{j['e']}-{j['kind']}-1080x1350.jpg"))
if 'carousel' in PARTS:
    for e, sl in CAR.items(): jobs += nc.jobs_for(e, sl, OUT / 'carousel')
if 'stories' in PARTS:
    for j in S['stories']:
        jobs.append(dict(j, out=OUT / 'stories' / f"{j['kind']}-{j['e']}-1080x1920.jpg"))
        jobs.append(dict(j, guide=True, out=OUT / 'previews' / 'stories-guides' / f"{j['kind']}-{j['e']}-guide.jpg"))
    for e in S['story_expert']:
        jobs.append({'e': e, 'kind': 'story-expert', 'out': OUT / 'stories' / 'experts' / f"{e}-story-expert-1080x1920.jpg"})
    jobs.append({'e': 'asya', 'kind': 'story-expert', 'guide': True, 'out': OUT / 'previews' / 'stories-guides' / 'story-expert-asya-guide.jpg'})
if 'highlights' in PARTS:
    for e in S['highlights']:
        k = 'highlight-start' if e == 'start' else 'highlight'
        jobs.append({'e': 'asya' if e == 'start' else e, 'kind': k, 'out': OUT / 'highlights' / f"{'00-start' if e == 'start' else e}-highlight-1080x1920.jpg"})
if 'reels' in PARTS:
    for e, t in SX.items():
        jobs.append({'e': e, 'kind': 'reels-cover', 't': t, 'out': OUT / 'reels' / 'covers' / f"{e}-reels-cover-1080x1920.jpg"})
        jobs.append({'e': e, 'kind': 'reels-frame', 't': t, 'out': OUT / 'reels' / 'frames' / f"{e}.png"})
        jobs.append({'e': e, 'kind': 'reels-end', 'out': OUT / 'reels' / 'end' / f"{e}-reels-end-1080x1920.jpg"})
    jobs.append({'e': 'eva', 'kind': 'reels-end', 'guide': True, 'out': OUT / 'previews' / 'reels-end-guide.jpg'})
res = asyncio.run(np_.render_many(jobs))
bad = [r['out'] for r in res if not r['ok']]
print(len(res), 'rendered,', len(bad), 'bad', *bad)
sys.exit(1 if bad else 0)
