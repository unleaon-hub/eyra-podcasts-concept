# EYRA · Pinterest

Главная картинка: `pinterest-overview.png`. Макет профиля: `previews/mock-profile.png`. Тексты и план досок: `TEXTS.md`.

| Папка / файл | Что это | Куда |
|---|---|---|
| `profile/avatar-800.png` | Аватар-полосы (как на всех площадках) | Профиль → фото |
| `profile/profile-cover-1600x900.jpg` | Обложка профиля 16:9 | Профиль → обложка (бизнес-аккаунт) |
| `board-covers/<id>-board-cover-1000x1500.jpg` | Обложки 10 досок | Пин в доску, потом выбрать его обложкой |
| `pins/<id>-<slug>-pin-1000x1500.jpg` | Пины, вариант А (основной) | Пины по доскам (план — `TEXTS.md`) |
| `alt-b/` | Запасной вариант Б «рамка-открытка», по одному на эксперта | Не основной стиль, на случай смены |
| `previews/` | Макет профиля и кадр квадратной обложки | Для проверки |

Новый пин: `python3 ../scripts/pinterest/new-pin.py <id> "Заголовок" ["подстрока"]` (`--kind board` — обложка доски, `--kind alt-b` — вариант Б).
Все пины заново: `python3 ../scripts/pinterest/render-all.py` (берёт список из `scripts/pinterest/pins.tsv`).

## Требования Pinterest (проверено 18.11.2026)

| Что | Требование | Источник |
|---|---|---|
| Обычный пин | 2:3, 1000×1500; выше 2:3 может обрезаться в ленте | https://help.pinterest.com/en/business/article/pinterest-product-specs |
| Файл | BMP, JPEG, PNG, TIFF, WEBP; до 20 МБ с компьютера; всё переводится в 8-бит sRGB JPEG | https://help.pinterest.com/en/article/review-pin-specs |
| Белый фон | На почти белые пины в светлой теме ложится слой #000 4% | там же |
| Видео-пин | MP4/M4V (в приложении и MOV), H.264/H.265, 4 с – 5 мин; полный экран 9:16 1080×1920 | там же |
| Безопасные зоны полноэкранного пина | сверху 270, слева 65, справа 195, снизу 790 px | там же |
| Название / текст-блок / описание | 100 / 250 / 800 символов; в ленте видно ~40 символов названия | там же; product-specs |
| Обложка доски | Выбирается из пинов доски; в профиле — квадратная плитка; на Android не меняется | https://help.pinterest.com/en/article/edit-a-board |
| Обложка профиля | Только бизнес-аккаунт; от 800×450, 16:9 | https://help.pinterest.com/en/business/article/personalize-your-profile |
| Фото профиля | Размер не указан; показывается кругом | https://help.pinterest.com/en/article/edit-your-profile |
