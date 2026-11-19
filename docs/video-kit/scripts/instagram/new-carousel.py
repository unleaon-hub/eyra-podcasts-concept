#!/usr/bin/env python3
"""EYRA · карусели Instagram из carousels.tsv (по строке на слайд) -> ../../instagram/carousel/<id>/<id>-N-of-M-1080x1350.jpg

  python3 new-carousel.py              # все 10 каруселей
  python3 new-carousel.py asya kira    # только эти эксперты
  python3 new-carousel.py --tsv my.tsv --out /tmp/car   # свой файл и папка

Слайды: carcover (обложка: сцена + вопрос), tip (совет; номер 01, 02… ставится сам), meet («Кто такая …»), cta (Telegram + 7 дней бесплатно + без карты).
Для meet и cta тексты берутся с eyra.ink (site.js). Печатает OK/BAD; с BAD не публиковать — сократите текст в TSV.
"""
import argparse, asyncio, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('np', HERE / 'new-post.py'); np_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(np_)

def read_tsv(path):
    car = {}
    for line in open(path, encoding='utf-8'):
        if not line.strip() or line.startswith('#'): continue
        c = (line.rstrip('\n').split('\t') + ['', '', ''])[:4]
        car.setdefault(c[0], []).append({'kind': c[1], 't': c[2], 'b': c[3]})
    return car

def jobs_for(e, slides, out):
    N = len(slides); tip = 0; jobs = []
    for i, s in enumerate(slides, 1):
        j = {'e': e, 'kind': s['kind'], 'pg': f'{i} / {N}', 'out': out / e / f'{e}-{i}-of-{N}-1080x1350.jpg'}
        if s['kind'] == 'carcover': j.update(t=s['t'], p=s['b'])
        elif s['kind'] == 'tip': tip += 1; j.update(t=s['t'], b=s['b'], n=f'{tip:02d}')
        elif s['kind'] == 'meet': j.update(k=s['t'] or ('Кто такая ' + np_.SITE[e]['name']), b=s['b'] or np_.SITE[e]['desc'])
        elif s['kind'] == 'cta': pass
        else: j.update(t=s['t'], b=s['b'])
        jobs.append(j)
    return jobs

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('experts', nargs='*'); a.add_argument('--tsv', default=str(HERE / 'carousels.tsv')); a.add_argument('--out', default=str(HERE.parent.parent / 'instagram' / 'carousel'))
    x = a.parse_args(); car = read_tsv(x.tsv); out = Path(x.out); jobs = []
    for e, sl in car.items():
        if x.experts and e not in x.experts: continue
        jobs += jobs_for(e, sl, out)
    res = asyncio.run(np_.render_many(jobs)); bad = [r['out'] for r in res if not r['ok']]
    print(len(res), 'slides,', len(bad), 'bad', *bad)
    raise SystemExit(1 if bad else 0)

if __name__ == '__main__':
    main()
