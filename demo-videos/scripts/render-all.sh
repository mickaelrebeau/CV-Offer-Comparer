#!/usr/bin/env bash
# Rend les 6 démos (3 vidéos × FR/EN) et publie les fichiers web de la landing :
#   frontend/public/videos/<démo>[-en].{mp4,webm} + <démo>[-en]-poster.webp
# Prérequis : Node (npx), ffmpeg (libx264, libvpx-vp9), cwebp.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=../frontend/public/videos
HF="npx -y hyperframes@0.8.80"
mkdir -p renders "$OUT"

# Plan hero de chaque démo, utilisé comme poster (avant lecture / mouvement réduit)
poster_at() {
  case "$1" in
    analyse) echo 9.6 ;;
    entretien) echo 13.0 ;;
    lettre) echo 12.9 ;;
  esac
}

for demo in analyse entretien lettre; do
  for lang in fr en; do
    suffix=""
    if [ "$lang" = "en" ]; then suffix="-en"; fi
    master="renders/$demo-$lang.mp4"
    name="$demo$suffix"

    $HF render --variables "{\"demo\":\"$demo\",\"lang\":\"$lang\"}" --strict-variables -o "$master"

    # Web : H.264 (Safari) et VP9, sans piste audio, 1920×1080 pour les écrans Retina
    ffmpeg -v error -y -i "$master" -an -c:v libx264 -preset slow -crf 30 -profile:v high \
      -pix_fmt yuv420p -movflags +faststart "$OUT/$name.mp4"
    ffmpeg -v error -y -i "$master" -an -c:v libvpx-vp9 -crf 40 -b:v 0 -row-mt 1 \
      -deadline good -cpu-used 2 "$OUT/$name.webm"
    ffmpeg -v error -y -ss "$(poster_at "$demo")" -i "$master" -frames:v 1 "renders/$name-poster.png"
    cwebp -quiet -q 82 "renders/$name-poster.png" -o "$OUT/$name-poster.webp"

    printf '%s : ok\n' "$name"
  done
done
