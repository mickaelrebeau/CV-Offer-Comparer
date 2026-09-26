#!/bin/sh
set -eu
# Pas de -s : dist/serve.json (généré au build) ne réécrit que les routes SPA
exec serve dist -l "tcp://0.0.0.0:${PORT:-3000}"
