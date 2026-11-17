#!/usr/bin/env bash
# EYRA · вертикальный тизер для Дзен «Ролики» (и VK Клипов / Shorts): кадр 1080×1920 + живая волна + прогресс.
# Использование:  ./make-vertical-teaser.sh <аудио> <эксперт> [выход.mp4]
#   эксперт: asya kira vera lera mira nika eva maya sofia alisa
# Отрезок аудио: START=<сек> (с какого места, по умолчанию 0), LEN=<сек> (длина, по умолчанию 60; Ролики Дзена — от 5 до 120 с)
# Пример:  START=754 LEN=45 ./make-vertical-teaser.sh ep12.wav asya ep12-asya-teaser.mp4
# Свой кадр с названием выпуска: FRAME=/путь/кадр.png (python3 new-cover.py asya "Название" --kind vertical-frame)
# Громкость: по умолчанию выравнивается до −14 LUFS (Дзен просит тише −12 LUFS); LOUD=0 — оставить как есть.
# Выход: MP4 1080×1920, H.264 High yuv420p 30 к/с, AAC 48 кГц стерео 192 кбит/с, faststart.
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,10p' "$0"; exit 1; }
AUDIO=$1; E=$2; OUT=${3:-${AUDIO%.*}-$E-teaser.mp4}
DIR=$(cd "$(dirname "$0")/.." && pwd)
FRAME=${FRAME:-$DIR/dzen/roliki/frames/$E.png}
ROW=$(awk -v e="$E" '$1==e' "$DIR/dzen/roliki/layout.tsv")
[ -n "$ROW" ] || { echo "Неизвестный эксперт: $E"; exit 1; }
[ -f "$FRAME" ] || { echo "Нет кадра: $FRAME"; exit 1; }
read -r _ WX WY WW WH BX BY BW BH C <<<"$ROW"
# кадр из new-cover.py --kind *frame кладёт рядом <кадр>.layout: там волна стоит под его названием
SIDE="${FRAME%.*}.layout"; [ -f "$SIDE" ] && read -r WX WY WW WH BX BY BW BH < "$SIDE"
START=${START:-0}; LEN=${LEN:-60}
TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO")
DUR=$(awk -v t="$TOTAL" -v s="$START" -v l="$LEN" 'BEGIN{d=t-s; if(d>l)d=l; if(d>120)d=120; printf "%.3f", d}')
awk -v d="$DUR" 'BEGIN{exit !(d>=5)}' || { echo "Отрезок короче 5 с — Дзен такой ролик не примет"; exit 1; }
FPS=30; PRESET=${PRESET:-medium}; CRF=${CRF:-20}
NORM=""; [ "${LOUD:-1}" = "1" ] && NORM="loudnorm=I=-14:TP=-1.5:LRA=11,"
FO=$(awk -v d="$DUR" 'BEGIN{printf "%.3f", d-0.8}')
echo "→ $E · ${DUR} с с ${START} с · $OUT"
ffmpeg -hide_banner -loglevel warning -stats -y \
  -loop 1 -framerate $FPS -i "$FRAME" -ss "$START" -t "$DUR" -i "$AUDIO" \
  -filter_complex "\
[1:a]${NORM}afade=t=in:st=0:d=0.3,afade=t=out:st=${FO}:d=0.8,aresample=48000,asplit=2[aout][a2];\
[a2]aformat=sample_fmts=fltp:channel_layouts=mono,showwaves=s=${WW}x${WH}:mode=cline:rate=${FPS}:scale=sqrt:draw=full:colors=0x${C},format=rgba,colorchannelmixer=aa=0.75[wv];\
color=c=0x${C}:s=${BW}x${BH}:r=${FPS},format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(X,W*T/${DUR}),235,0)'[bar];\
[0:v]scale=1080:1920,format=rgb24[bg];[bg][wv]overlay=${WX}:${WY}:shortest=1[v1];[v1][bar]overlay=${BX}:${BY}:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map "[aout]" -t "$DUR" \
  -c:v libx264 -preset "$PRESET" -crf "$CRF" -profile:v high -level 4.2 -pix_fmt yuv420p -r $FPS -g $((FPS*2)) -bf 2 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart "$OUT"
echo "✓ $OUT"
