#!/bin/sh
set -eu
exec serve -s dist -l "tcp://0.0.0.0:${PORT:-3000}"
