#!/usr/bin/env python3
"""Пересобрать весь набор Instagram из set.json в ../../instagram/ (grid/, carousel/, stories/, highlights/, reels/)."""
import asyncio, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('np', HERE / 'new-post.py'); np_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(np_)
OUT = HERE.parent.parent / 'instagram'; S = json.load(open(HERE / 'set.json', encoding='utf-8')); SX = {}
for line in open(HERE / 'sdata.js', encoding='utf-8'):
    if ':{name:' in line:
        e = line.split(':')[0].strip(); SX[e] = line.split("thumb:'")[1].split("'")[0].replace('&nbsp;', ' ')
jobs = []
for i, j in enumerate(S['grid'], 1):
    jobs.append(dict(j, out=OUT / 'grid' / f"{i:02d}-{j['e']}-{j['kind']}-1080x1350.jpg"))
for i, j in enumerate(S['carousel'], 1):
    jobs.append(dict(j, out=OUT / 'carousel' / f"maya-{i}-of-6-1080x1350.jpg"))
for j in S['stories']:
    jobs.append(dict(j, out=OUT / 'stories' / f"{j['kind']}-{j['e']}-1080x1920.jpg"))
    jobs.append(dict(j, guide=True, out=OUT / 'previews' / 'stories-guides' / f"{j['kind']}-{j['e']}-guide.jpg"))
for e in S['highlights']:
    jobs.append({'e': e, 'kind': 'highlight', 'out': OUT / 'highlights' / f"{e}-highlight-1080x1920.jpg"})
for e, t in SX.items():
    jobs.append({'e': e, 'kind': 'reels-cover', 't': t, 'out': OUT / 'reels' / 'covers' / f"{e}-reels-cover-1080x1920.jpg"})
    jobs.append({'e': e, 'kind': 'reels-frame', 't': t, 'out': OUT / 'reels' / 'frames' / f"{e}.png"})
res = asyncio.run(np_.render_many(jobs))
bad = [r['out'] for r in res if not r['ok']]
print(len(res), 'rendered,', len(bad), 'bad', *bad)
