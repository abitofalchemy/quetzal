# quetzal

Repo: https://github.com/abitofalchemy/quetzal

## Rules for all coding work
- **Audience:** guided by someone with advanced Python knowledge. Skip the basics.
- **Responses:** concise, compact, minimal.
- **Reproducible:** code must work from a fresh clone of this repo.
  - Manage dependencies with `uv`; commit `pyproject.toml` and `uv.lock`.
  - Pin model IDs and revisions. Document every run command.
  - Never rely on untracked local state. Secrets go in `.env` only (gitignored).
- **Git:** `git add`, commit and push to `origin/main` every 30 minutes while work is in progress.
  - Review staged files first. Never commit secrets, weights or `.venv`.

## Target hardware
RTX 4050 Mobile (6 GB VRAM), 7.5 GB RAM, no swap, Linux. Python 3.12 via uv.
