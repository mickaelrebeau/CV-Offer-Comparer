#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/../frontend/public/videos"
TMP="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT

mkdir -p "$OUT"
cd "$ROOT"

npm run render:analyse
npm run render:entretien
npm run render:posters

# Remotion H.264 ships with yuvj420p + silent AAC, which breaks Safari/iOS.
# Re-encode to web-safe H.264 Main / VP9 without audio.
for name in analyse entretien; do
  src="$OUT/${name}.mp4"

  ffmpeg -y -i "$src" \
    -vf "scale=1920:1080:flags=bicubic,format=yuv420p" \
    -c:v libx264 -profile:v main -level 4.0 -pix_fmt yuv420p \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    -preset slow -crf 24 -an -movflags +faststart \
    "$TMP/${name}.mp4"

  ffmpeg -y -i "$TMP/${name}.mp4" \
    -c:v libvpx-vp9 -pix_fmt yuv420p -crf 32 -b:v 0 -an \
    "$TMP/${name}.webm"

  mv "$TMP/${name}.mp4" "$OUT/${name}.mp4"
  mv "$TMP/${name}.webm" "$OUT/${name}.webm"
done

echo "Assets écrits dans $OUT"
ls -lh "$OUT"
