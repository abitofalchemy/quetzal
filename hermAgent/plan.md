# Plan for the setup and configuration of Hermes Agent 

1. Document the process from ideation to deployment.
2. The goal is to setup a Hermes client on this system.
3. Allow Hermes minimal tools that can be accessed.
4. Configure hermes to be reproducible if I had to start from scratch.
5. Use a combination of tools like uv (from Astral) and Python and any Linux gnu tools in a way that is reproducible.
6. Keep a how to set this up article that can be posted and optimized for LinkedIn posts. Do this in local docs/ folder.
7. Keep unittests to ensure this is gradually working to a final state.
8. Keep scripts that log the performance on this system. 

## Decisions (Q&A, 2026-11-03)

Answers to the setup questions, so a rebuild makes the same choices.

| # | Question | Answer | Why |
|---|---|---|---|
| 1 | Which Hermes? | NousResearch `hermes-agent` 0.19.0 (PyPI) | Official agent; pinnable |
| 2 | Will Ollama work on the final platform (Mac mini M4 Pro, 24 GB)? | Yes: the GPU can use about 16 GB, enough for a 4–8B model at 64K context | The Mac is the deployment target |
| 3 | Can I prototype on this Linux box first? | Yes: RTX 4050 laptop, model hosted remotely | The Linux GPU is unusable (`nvidia_uvm` missing); the hosted model needs no GPU |
| 4 | Hosted or local LLM? | **OpenRouter on both machines**; Ollama available as an option | Same setup everywhere; better tool calling |
| 5 | A flag for the deployment hardware? | Yes: `--target linux-dev\|mac-m4` (auto-detected) plus a separate `--backend openrouter\|ollama` | Changing the backend doesn't change the machine settings |
| 6 | OpenRouter model? | `qwen/qwen3-30b-a3b-instruct-2507` (262K context) | Hermes requires ≥ 64K context; `qwen3-14b` has only 41K |
| 7 | Ollama model? | `qwen3:4b-instruct-2507`, 64K context, q8 KV cache | About 7.5 GB total (estimate); fits the Mac with room to spare |
| 8 | Which tools? | `file` + `terminal` only; approvals `manual`; cron `deny` | Smallest useful agent |
| 9 | How to install? | `uv`, pinned in `pyproject.toml` + `uv.lock` | Reproducible; no curl installer |
| 10 | Where do commits go? | `quetzal` repo under `hermAgent/`, `origin/main` | Per `CLAUDE.md` |
| 11 | Which keys are needed? | `OPENROUTER_API_KEY` in `.env` only (set a credit limit on it) | Ollama needs none; other Hermes tools are disabled. A GitHub token is needed only to push |

