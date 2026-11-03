#!/usr/bin/env bash
# Log performance for this machine. Extra args go to `hagent perf` (e.g. --runs 5 --no-agent).
set -euo pipefail
cd "$(dirname "$0")/.."
exec uv run hagent ${TARGET:+--target "$TARGET"} ${BACKEND:+--backend "$BACKEND"} perf "$@"
