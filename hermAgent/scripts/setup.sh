#!/usr/bin/env bash
# Fresh-clone bootstrap. Portable: bash 3.2 (macOS) and GNU bash; no GNU-only flags.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v uv >/dev/null || { echo "install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
uv sync --frozen                      # exact versions from uv.lock
[ -f .env ] || { cp .env.example .env; echo "created .env — add OPENROUTER_API_KEY"; }
uv run hagent render
uv run pytest -q
uv run hagent doctor || echo "doctor reported issues (see above)"
