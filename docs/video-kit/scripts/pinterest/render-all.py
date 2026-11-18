#!/usr/bin/env python3
"""Пересобрать все пины и обложки досок из pins.tsv в ../../pinterest/ (pins/, board-covers/, alt-b/)."""
import asyncio, csv, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('np', HERE / 'new-pin.py'); np_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(np_)
OUT = HERE.parent.parent / 'pinterest'
jobs, seen = [], set()
for r in csv.reader((l for l in open(HERE / 'pins.tsv', encoding='utf-8') if not l.startswith('#')), delimiter='\t'):
    kind, e, board, title, sub = r[:5]
    if kind == 'board':
        jobs.append((e, title, '', 'board', OUT / 'board-covers' / f'{e}-board-cover-1000x1500.jpg'))
    else:
        jobs.append((e, title, sub, 'pin', OUT / 'pins' / f'{e}-{np_.slug(title)}-pin-1000x1500.jpg'))
        if e not in seen:  # one alt «рамка» per expert
            seen.add(e); jobs.append((e, title, sub, 'alt-b', OUT / 'alt-b' / f'{e}-{np_.slug(title)}-pin-B-1000x1500.jpg'))
for d in ('pins', 'board-covers', 'alt-b'): (OUT / d).mkdir(parents=True, exist_ok=True)
res = asyncio.run(np_.render_many(jobs))
bad = [r['out'] for r in res if not r['ok']]
print(len(res), 'rendered,', len(bad), 'bad', *bad)
