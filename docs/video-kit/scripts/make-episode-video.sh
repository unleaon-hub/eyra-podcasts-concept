#!/usr/bin/env bash
# EYRA · видео для аудио-выпуска: кадр эксперта + живая волна + тонкий прогресс.
# Использование:  ./make-episode-video.sh <аудио> <эксперт> [выход.mp4]
#   эксперт: asya kira vera lera mira nika eva maya sofia alisa
# Пример:         ./make-episode-video.sh ep12.wav asya ep12-asya.mp4
# Своя картинка кадра (например, с названием выпуска): FRAME=/путь/кадр.png ./make-episode-video.sh ...
# Выход: MP4 1920×1080, H.264 High yuv420p 30 к/с, AAC 48 кГц стерео 256 кбит/с, faststart — подходит для YouTube и RUTUBE.
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,8p' "$0"; exit 1; }
AUDIO=$1; E=$2; OUT=${3:-${AUDIO%.*}-$E.mp4}
DIR=$(cd "$(dirname "$0")/.." && pwd)
FRAME=${FRAME:-$DIR/video-frame/frames/$E.png}
ROW=$(awk -v e="$E" '$1==e' "$DIR/video-frame/layout.tsv")
[ -n "$ROW" ] || { echo "Неизвестный эксперт: $E"; exit 1; }
[ -f "$FRAME" ] || { echo "Нет кадра: $FRAME"; exit 1; }
read -r _ WX WY WW WH BX BY BW BH C <<<"$ROW"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO")
FPS=30; PRESET=${PRESET:-medium}; CRF=${CRF:-20}
echo "→ $E · $(printf '%.0f' "$DUR") с · $OUT"
ffmpeg -hide_banner -loglevel warning -stats -y \
  -loop 1 -framerate $FPS -i "$FRAME" -i "$AUDIO" \
  -filter_complex "\
[1:a]aformat=sample_fmts=fltp:channel_layouts=mono,showwaves=s=${WW}x${WH}:mode=cline:rate=${FPS}:scale=sqrt:draw=full:colors=0x${C},format=rgba,colorchannelmixer=aa=0.75[wv];\
color=c=0x${C}:s=${BW}x${BH}:r=${FPS},format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(X,W*T/${DUR}),235,0)'[bar];\
[0:v]format=rgb24[bg];[bg][wv]overlay=${WX}:${WY}:shortest=1[a1];[a1][bar]overlay=${BX}:${BY}:shortest=1,\
format=yuv420p[v]" \
  -map "[v]" -map 1:a -t "$DUR" \
  -c:v libx264 -preset "$PRESET" -crf "$CRF" -profile:v high -level 4.1 -pix_fmt yuv420p -r $FPS -g $((FPS*2)) -bf 2 \
  -c:a aac -b:a 256k -ar 48000 -ac 2 \
  -movflags +faststart "$OUT"
echo "✓ $OUT"
