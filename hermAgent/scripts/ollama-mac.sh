#!/usr/bin/env bash
# Optional local backend on the Mac. Serves with 64K context + q8 KV cache (Hermes minimum).
set -euo pipefail
command -v ollama >/dev/null || { echo "install: brew install ollama"; exit 1; }
MODEL="$(uv run python -c 'from hermagent.profiles import load; print(load()["backends"]["ollama"]["model"])')"
export OLLAMA_CONTEXT_LENGTH=65536 OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0
# If the Ollama.app is already running it ignores these vars: quit it, or `launchctl setenv OLLAMA_CONTEXT_LENGTH 65536` and relaunch.
pgrep -x ollama >/dev/null || { ollama serve >/tmp/ollama.log 2>&1 & sleep 3; }
ollama pull "$MODEL"
echo "ready: uv run hagent --backend ollama chat"
