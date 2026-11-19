#!/usr/bin/env python3
"""Build Threads texts (THREADS.md + threads-texts.tsv) from site.js, carousels.tsv and threads.json.
Checks every post against the 500-character limit (emoji counted by UTF-8 bytes, as Meta's API docs say).
Usage: python3 mktexts.py [out_dir]   (default: ../../threads next to this kit)"""
import csv, json, os, re, sys, unicodedata
from pathlib import Path
HERE = Path(__file__).resolve().parent
IG = next(p for p in (HERE.parent / 'instagram', HERE.parent / 'ig') if (p / 'site.js').exists())
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get('TH_OUT', HERE.parents[1] / 'threads')); OUT.mkdir(parents=True, exist_ok=True)
s = open(IG / 'site.js', encoding='utf-8').read()
SITE = json.loads(s.split('window.SITE=')[1].split(';\nwindow.OFFER=')[0])
O = json.loads(s.split('window.OFFER=')[1].rsplit(';', 1)[0])
D = json.load(open(HERE / 'threads.json', encoding='utf-8'))
NB = lambda t: t.replace('&nbsp;', ' ').replace('\u00a0', ' ')
CAR = {}
for r in csv.reader(open(IG / 'carousels.tsv', encoding='utf-8'), delimiter='\t'):
    if not r or r[0].startswith('#'): continue
    e, k = r[0], r[1]; CAR.setdefault(e, {'tips': []})
    if k == 'carcover': CAR[e]['cover'] = (NB(r[2]), NB(r[3]))
    if k == 'tip': CAR[e]['tips'].append((NB(r[2]), NB(r[3])))
ORDER = ['asya', 'kira', 'vera', 'lera', 'mira', 'nika', 'eva', 'maya', 'sofia', 'alisa']
OFFER = f"{O['free']} · {O['nocard']}"

def tlen(t):  # emoji = UTF-8 bytes, everything else = 1
    return sum(len(c.encode()) if unicodedata.category(c) == 'So' and ord(c) > 0x2BFF else 1 for c in t)

def question(t):
    return t + '?' if re.match(r'^(Как|Что|С чего|Куда|Где|Когда|Зачем|Почему)\b', t) else t

POSTS = []  # (section, id, kind, media, text)
def add(sec, i, kind, media, text): POSTS.append((sec, i, kind, media, text))

add('pinned', 'pinned', 'закреп · карусель 3 фото', 'instagram/pinned/1-pin-about, 2-pin-how, 3-pin-offer (-1080x1350.jpg)',
    f"{O['hero']}\n{O['heroSub']}\n\n{O['how']}\n" + '\n'.join(f"{n}. {a}" for n, (a, b) in enumerate(O['steps'], 1)) +
    f"\n\n{OFFER}\n{O['after']} {O['after2']}\n{O['several']}\n\nhttps://eyra.ink/")
for e in ORDER:
    S = SITE[e]; C = CAR[e]; X = D['experts'][e]; t, b = C['cover']
    add(e, f'{e}-1', 'тред · пост 1 (фото)', f'threads/posts/{e}-post-1080x1350.jpg', f"{question(t)}\n{b} — в ветке ниже.")
    for n, (a, bb) in enumerate(C['tips'], 1):
        add(e, f'{e}-{n+1}', f'тред · ответ {n}', '', f"{n}/{len(C['tips'])} · {a}\n{bb}")
    add(e, f'{e}-cta', 'тред · финал (ссылка → превью)', f'превью ссылки = og:image страницы (предложение: threads/link-preview/og-{e}-1200x630.jpg)',
        f"{S['name']} · {S['role']}. {S['desc']}\n{O['chat']}.\n\n{OFFER}\n{O['after']} {O['after2']}\n\n{S['cta']} → {S['url']}")
    add(e, f'{e}-carousel', 'отдельный пост · карусель Instagram 7 фото (по желанию)', f'instagram/carousel/{e}/ (1…7-of-7-1080x1350.jpg)',
        f"{question(t)}\n{b} — листайте карусель.\n{OFFER}\n{S['url']}")
    add(e, f'{e}-quote', 'отдельный пост · цитата (фото)', f'threads/quotes/{e}-quote-1080x1350.jpg',
        f"{S['benefit']}\n{S['name']} · {S['role']} — {O['chat'][0].lower() + O['chat'][1:]}.\n{OFFER}\n{S['url']}")
for n, p in enumerate(D['polls'], 1):
    S = SITE[p['e']]
    add('polls', f'poll-{n}', 'опрос (2–4 варианта, до 25 симв.)', ' / '.join(p['options']), p['text'])

bad = [(i, tlen(t)) for _, i, _, _, t in POSTS if tlen(t) > 500]
bad += [(f"poll option {o}", len(o)) for p in D['polls'] for o in p['options'] if len(o) > 25]
bad += [(f"topic {e}", X['topic']) for e, X in D['experts'].items() if not (1 <= len(X['topic']) <= 50) or re.search(r'[.&]', X['topic'])]
if tlen(D['bio']) > 150: bad.append(('bio', tlen(D['bio'])))

with open(OUT / 'threads-texts.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['section', 'id', 'kind', 'media', 'chars', 'text'])
    for sec, i, k, m, t in POSTS: w.writerow([sec, i, k, m, tlen(t), t])

L = ['# EYRA · Threads — тексты и порядок публикации', '',
     '**Статус: ЧЕРНОВИК — согласовать перед публикацией.** Оффер, имена, роли, «Когда хочется…», описания и шаги — дословно с https://eyra.ink/ (через `scripts/instagram/site.js`); советы — из Instagram-каруселей (`carousels.tsv`). Каждый пост проверен на лимит Threads 500 символов (эмодзи считаются по байтам UTF-8). Генерирует `scripts/threads/mktexts.py`, таблица для копирования — `threads-texts.tsv`.', '',
     '## 1. Профиль', '', '| Поле | Текст | Длина |', '|---|---|---|',
     f"| Имя | {D['name']} (в Threads имя и аватар можно импортировать из Instagram) | {len(D['name'])} |",
     f"| Имя пользователя | совпадает с Instagram — в макете `{D['handle']}`, уточнить | |",
     f"| Описание | {D['bio'].replace(chr(10), '<br>')} | {tlen(D['bio'])} из 150* |",
     f"| Ссылки (до 5) | {', '.join(D['links'])} — по желанию добавьте ссылки на ботов (таблица ниже) | |",
     '| Фото профиля | `instagram/profile/avatar-800.png` или «Импорт из Instagram» | |', '',
     '\\* Лимит 150 символов Meta официально не публикует; это значение из сторонних справочников — держим описание короче.', '',
     '## 2. Закреплённый пост (в профиле можно закрепить только 1)', '']
def block(i, k, m, t):
    L.extend([f"**{i}** · {k}" + (f" · медиа: `{m}`" if m else '') + f" · {tlen(t)}/500", '', '```', t, '```', ''])
for sec, i, k, m, t in POSTS:
    if sec == 'pinned': block(i, k, m, t)
L += ['## 3. Треды экспертов (хук + 4 ответа + финал), карусели и посты-цитаты', '',
      'Публикуйте пост 1 с фото, затем ответами к нему — советы 1–4 и финал со ссылкой (первая ссылка в тексте превращается в превью с og:image страницы эксперта). Тему (topic) ставьте в поле «Добавить тему» — одна на пост.', '']
for e in ORDER:
    S = SITE[e]; X = D['experts'][e]
    L += [f"### {S['name']} · {S['role']} — тема «{X['topic']}»", '', f"Бот: {S['bot']} · страница: {S['url']}", '']
    for sec, i, k, m, t in POSTS:
        if sec == e: block(i, k, m, t)
L += ['## 4. Опросы (по желанию)', '', 'Опрос — 2–4 варианта по 1–25 символов; работает 24 часа (по сторонним источникам). Нельзя совместить с вложением-текстом.', '']
for sec, i, k, m, t in POSTS:
    if sec == 'polls': block(i, k, m, t)
L += ['## 5. Порядок на первые две недели', '', '1. Закреп (карусель из трёх закрепов Instagram) → «Закрепить в профиле».',
      '2. По одному треду эксперта в день, в порядке сайта: Ася, Кира, Вера, Лера, Мира, Ника, Ева, Майя, София, Алиса.',
      '3. Между тредами — посты-цитаты и опросы; карусели из `instagram/carousel/` (4:5) можно выкладывать как есть.',
      '4. Текст можно исправить в течение 15 минут после публикации — проверяйте сразу.', '']
(OUT / 'threads-texts.js').write_text('window.TT=' + json.dumps({i: t for _, i, _, _, t in POSTS}, ensure_ascii=False, indent=0) + ';\nwindow.TD=' + json.dumps({k: D[k] for k in ('handle', 'name', 'bio', 'links')}, ensure_ascii=False) + ';\n', encoding='utf-8')
(OUT / 'THREADS.md').write_text('\n'.join(L), encoding='utf-8')
print(f'{len(POSTS)} posts, max {max(tlen(t) for *_, t in POSTS)} chars ->', OUT)
if bad: print('OVER LIMIT:', bad); sys.exit(1)
