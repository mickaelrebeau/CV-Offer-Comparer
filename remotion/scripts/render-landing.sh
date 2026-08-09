#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/../frontend/public/videos"

mkdir -p "$OUT"
cd "$ROOT"

npm run render:landing

echo "Assets écrits dans $OUT"
