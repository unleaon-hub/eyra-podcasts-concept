#!/usr/bin/env python3
"""EYRA · Instagram: пост, слайд карусели, сторис, обложка/кадр Reels или обложка «Актуального» в светлом стиле.

  python3 new-post.py alisa "Что написать после свидания"                              -> пост 1080×1350 (сцена + вопрос)
  python3 new-post.py eva "Когда среда не работает" "как выйти из круга знакомств"      -> с подстрокой
  python3 new-post.py nika "Рассказать о себе — …" --kind quote                         -> карточка-цитата
  python3 new-post.py maya "Как восстановиться за выходной" --kind carcover --pill "4 идеи от Майи"
  python3 new-post.py maya "Начните с тишины" --kind tip --n 01 --body "Первый час — …" --pg "2 / 6"
  python3 new-post.py maya --kind final                                                  -> последний слайд карусели
  python3 new-post.py asya "Что помогает вам успокоиться вечером?" --kind story-question -> сторис 1080×1920
      (story-poll, story-episode, story-quote — так же; место под стикер оставлено, сам стикер ставится в приложении)
  python3 new-post.py eva "Как найти друзей взрослому" --kind reels-cover                -> обложка Reels 1080×1920
  python3 new-post.py eva "Как найти друзей взрослому" --kind reels-frame                -> кадр для тизера + .layout
  python3 new-post.py vera --kind highlight                                              -> обложка «Актуального»

--guide рисует безопасные зоны (для проверки, не публиковать). Печатает OK/BAD; с BAD не публиковать — сократите текст.
Нужно: Python 3, pip install playwright pillow; Chrome в системе или `playwright install chromium`.
"""
import argparse, asyncio, json, re, shutil, sys, urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
EXPERTS = 'asya kira vera lera mira nika eva maya sofia alisa'.split()
KINDS = 'post carcover quote tip final story-question story-poll story-episode story-quote reels-cover reels-frame highlight'.split()
HD = json.load(open(HERE / 'ibg.json'))

def slug(s):
    tr = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sch','','y','','e','yu','ya']))
    s = ''.join(tr.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'post'

def tall(kind): return kind.startswith('story') or kind.startswith('reels') or kind == 'highlight'

async def render_many(jobs):
    """jobs: list of dicts {e, kind, t, s, n, b, pg, p, guide, out}. Returns qa list."""
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    args = ['--allow-file-access-from-files', '--no-sandbox']; res = []
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=chrome, args=args) if chrome else p.chromium.launch(args=args))
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        errs = []; pg.on('pageerror', lambda x: errs.append(str(x)))
        for j in jobs:
            k = j['kind']; grp = 'story' if k.startswith('story') else 'reels' if k.startswith('reels') else 'post'
            q = {'m': k, 'e': j['e'], 'head': HD[grp][j['e']]['head']}
            for a in ('t', 's', 'n', 'b', 'pg', 'p'):
                if j.get(a): q[a] = j[a]
            if j.get('guide'): q['guide'] = '1'
            await pg.set_viewport_size({'width': 1080, 'height': 1920 if tall(k) else 1350})
            await pg.goto((HERE / 'ig.html').as_uri() + '?' + urllib.parse.urlencode(q))
            await pg.wait_for_selector('body[data-ready]', state='attached')
            qa = await pg.evaluate('qa'); out = Path(j['out']); out.parent.mkdir(parents=True, exist_ok=True)
            if out.suffix.lower() == '.png':
                await pg.screenshot(path=str(out))
            else:
                tmp = out.with_suffix('.tmp.png'); await pg.screenshot(path=str(tmp))
                Image.open(tmp).convert('RGB').save(out, quality=94, subsampling=0); tmp.unlink()
            if k == 'reels-frame' and not j.get('guide'):
                lay = await pg.evaluate('window.layout'); w = lay['wave']; t = lay['track']
                out.with_suffix('.layout').write_text(' '.join(str(round(v)) for v in w + t) + '\n')
            qa['ok'] = qa['bottom'] <= qa['limit'] and not errs; qa['out'] = str(out); res.append(qa)
            print('OK ' if qa['ok'] else 'BAD', out.name, 'fs', qa.get('fs'), 'gap', round(qa['limit'] - qa['bottom']) if k != 'highlight' else '-', *errs)
            errs.clear()
        await b.close()
    return res

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('expert', choices=EXPERTS); a.add_argument('text', nargs='?', default=''); a.add_argument('sub', nargs='?', default='')
    a.add_argument('--kind', choices=KINDS, default='post'); a.add_argument('--n'); a.add_argument('--body'); a.add_argument('--pg'); a.add_argument('--pill')
    a.add_argument('--guide', action='store_true'); a.add_argument('--out')
    x = a.parse_args()
    if x.kind not in ('final', 'highlight') and not x.text: a.error('нужен текст')
    ext = 'png' if x.kind == 'reels-frame' else 'jpg'; size = '1080x1920' if tall(x.kind) else '1080x1350'
    out = x.out or f"{x.expert}-{x.kind}-{slug(x.text) if x.text else x.kind}-{size}.{ext}"
    r = asyncio.run(render_many([{'e': x.expert, 'kind': x.kind, 't': x.text, 's': x.sub, 'n': x.n, 'b': x.body, 'pg': x.pg, 'p': x.pill, 'guide': x.guide, 'out': out}]))
    sys.exit(0 if r[0]['ok'] else 1)

if __name__ == '__main__':
    main()
