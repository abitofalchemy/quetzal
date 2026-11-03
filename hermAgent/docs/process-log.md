# Process log: from idea to deployment

## 1. Ideation (2026-11-03)
Goal (`plan.md`): run a Hermes Agent client with a minimal set of tools, set up reproducibly with `uv`. The work needs docs, tests, performance logs and a LinkedIn article.

## 2. Decisions
| Question | Decision | Why |
|---|---|---|
| Which Hermes | NousResearch `hermes-agent` 0.19.0 from PyPI | Pinned and installed with uv; skips the unpinned curl installer |
| Hardware | Prototype on Linux (RTX 4050, 6 GB), deploy on Mac mini M4 Pro (24 GB) | The Mac is the final platform |
| LLM | OpenRouter on both machines; Ollama optional | The Linux GPU is unusable (`nvidia_uvm` missing); hosted keeps both machines identical |
| Model | `qwen/qwen3-30b-a3b-instruct-2507` | Hermes requires ≥ 64K context, which rules out `qwen3-14b` (41K on OpenRouter); 262K context at $0.10/$0.30 per million tokens |
| Local model | `qwen3:4b-instruct-2507`, 64K context, q8 KV cache | About 7.5 GB total (estimate), well inside the Mac GPU's roughly 16 GB budget |
| Tools | `file` + `terminal`, approvals `manual`, cron `deny` | Smallest useful agent; the 20+ other toolsets are disabled |
| Hardware switch | `--target` (hardware) kept separate from `--backend` (LLM) | Switching the Mac to Ollama is a one-flag change |

## 3. Build
- `config/profiles.toml` is the single source of truth. `hagent render` writes the Hermes `config.yaml` into a Hermes home folder inside the project (`.hermes-home/`), so nothing depends on `~/.hermes`.
- Tests check target detection, backend override, the 64K context minimum, the toolset allowlist (as reported by `hermes tools list` itself) and the version pin.

## 4. Status
- [x] Linux: install, config and 13 offline tests pass
- [ ] Linux: live turn + perf baseline (needs `OPENROUTER_API_KEY`)
- [ ] Mac: `./scripts/setup.sh`, perf baseline (OpenRouter)
- [ ] Mac: Ollama backend measured (`./scripts/ollama-mac.sh`, `BACKEND=ollama ./scripts/perf.sh`)
