"""Render docs/architecture.png (high-level view of this Hermes setup on linux-dev).

Run:  uv run --no-project --with matplotlib==3.10.0 python scripts/architecture.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "docs" / "architecture.png"
W, H, DPI = 14, 7.875, 150  # 16:9, under the 16x9 in / 300 dpi limit

C = {"ink": "#1f2933", "mute": "#52606d", "line": "#7b8794", "host": "#f5f7fa",
     "cli": "#dbeafe", "cfg": "#fef3c7", "hermes": "#dcfce7", "tool": "#f0fdf4",
     "cloud": "#ede9fe", "perf": "#fce7f3", "violet": "#7c3aed", "dim": "#9aa5b1"}

fig = plt.figure(figsize=(W, H), dpi=DPI)
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 140); ax.set_ylim(0, 78.75); ax.axis("off")


def box(x, y, w, h, title, body="", fc="#fff", ec=None, ls="-", tsize=10.5, bsize=8.2, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
                                fc=fc, ec=ec or C["line"], lw=1.3, ls=ls, zorder=z))
    ax.text(x + 1.2, y + h - 1.3, title, ha="left", va="top", fontsize=tsize,
            weight="bold", color=C["ink"], zorder=z + 1)
    if body:
        ax.text(x + 1.2, y + h - 4.3, body, ha="left", va="top", fontsize=bsize,
                color=C["mute"], family="monospace", linespacing=1.45, zorder=z + 1)


def label(x, y, s, **kw):
    ax.text(x, y, s, ha="center", va="center", fontsize=7.8, color=C["ink"], zorder=7,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"), **kw)


def arrow(a, b, ls="-", color=None, both=False):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="<|-|>" if both else "-|>", mutation_scale=12,
                                 lw=1.4, ls=ls, color=color or C["line"], zorder=5))


def path(pts, ls="-", color=None):
    xs, ys = zip(*pts[:-1])
    ax.plot(xs, ys, ls=ls, color=color, lw=1.4, zorder=5)
    arrow(pts[-2], pts[-1], ls=ls, color=color)


# title
ax.text(2, 77, "hermAgent: Hermes Agent setup on this machine (target: linux-dev)",
        fontsize=15, weight="bold", color=C["ink"], va="top")
ax.text(2, 73.2, "One TOML file drives everything: `hagent` resolves (target, backend), renders the "
        "Hermes config, then execs `hermes chat`. The model runs on OpenRouter by default.",
        fontsize=9, color=C["mute"], va="top")

# host boundary
box(1.5, 1.5, 102, 68, "", fc=C["host"], ec=C["dim"], ls="--", z=0)
ax.text(3, 3.2, "Linux laptop (xubuntu)  ·  RTX 4050 Mobile 6 GB  ·  7.5 GB RAM  ·  "
        "Python 3.12 via uv (pyproject.toml + uv.lock)", fontsize=8.5, weight="bold",
        color=C["mute"], va="center")

# column 1: user + inputs
box(3, 54, 18, 11, "User / terminal",
    "uv run hagent chat\nuv run hagent doctor\n./scripts/perf.sh")
box(3, 36, 18, 14, "config/profiles.toml",
    "source of truth\nhermes 0.19.0\ntools: file+terminal\napprovals: manual\nctx >= 65536",
    fc=C["cfg"])
box(3, 22, 18, 10, ".env (gitignored)", "OPENROUTER_API_KEY", fc=C["cfg"])
box(3, 6, 18, 12, "platform.system()", "Linux\n -> linux-dev\nDarwin/arm64\n -> mac-m4",
    fc=C["cfg"])

# column 2: hagent
box(30, 34, 27, 31, "hagent CLI (src/hermagent)",
    "profiles.resolve()\n  target+backend -> Profile\n\nprofiles.render()\n  -> .hermes-home/config.yaml\n\n"
    "cli.build_env()\n  .env + HERMES_HOME\n\nrender | doctor | chat | perf", fc=C["cli"])
box(30, 20, 27, 10, ".hermes-home/config.yaml",
    "GENERATED, gitignored\nmodel: openrouter/qwen3-30b\nmemory off · cron: deny", fc=C["cfg"],
    bsize=7.8, tsize=10)
box(30, 6, 27, 10.5, "perf.py (hagent perf)",
    "-> perf/results/linux-dev.csv\nTTFT, tok/s, RSS, RAM, GPU", fc=C["perf"], bsize=7.8, tsize=10)

# column 3: hermes
box(62, 34, 36, 31, "Hermes Agent 0.19.0 (hermes chat)",
    "replaces hagent via os.execvpe\nHERMES_HOME=.hermes-home\n\nloop: prompt -> LLM -> tool calls",
    fc=C["hermes"])
box(64, 37, 15.5, 11.5, "file tools", "read/write\nfiles", fc=C["tool"], tsize=9.5)
box(81, 37, 15.5, 11.5, "terminal tools", "local shell\nmanual\napproval", fc=C["tool"],
    tsize=9.5)
box(62, 20, 36, 10, "Local filesystem & shell",
    "where tool calls take effect\n(no web, browser, memory, cron)")
box(62, 6, 36, 10.5, "Ollama @ localhost:11434 (optional)",
    "qwen3:4b-instruct-2507\n64K ctx, q8 KV cache", ls=":", tsize=10, bsize=7.8)

# cloud
box(108, 34, 30, 31, "OpenRouter (default)",
    "openrouter.ai/api/v1\nOpenAI-compatible API\n\nqwen/qwen3-30b-a3b-\n  instruct-2507\n262K context\n\n"
    "Bearer OPENROUTER_API_KEY", fc=C["cloud"])
ax.text(123, 30.5, "internet", ha="center", fontsize=9, color=C["mute"], style="italic")

# arrows
arrow((12, 53.6), (12, 50.4)); label(15.5, 52, "edit")
arrow((21.4, 59.5), (29.6, 59.5)); label(25.5, 59.5, "cmd")
arrow((21.4, 43), (29.6, 43)); label(25.5, 43, "load")
arrow((21.4, 27), (29.6, 37)); label(25.5, 32, "keys")
arrow((21.4, 12), (29.6, 35)); label(25.5, 23.5, "detect")
arrow((43.5, 33.6), (43.5, 30.4)); label(47.5, 32, "render")
arrow((57.4, 55), (61.6, 55)); label(59.5, 57.5, "exec")
arrow((57.4, 28), (63, 33.6)); label(58.5, 32, "reads")
arrow((71.5, 36.6), (71.5, 30.4), both=True)
arrow((88.5, 36.6), (88.5, 30.4), both=True)
arrow((98.4, 55), (107.6, 55), color=C["violet"], both=True); label(103, 57.5, "HTTPS")
# alternative backend (dotted)
path([(98.4, 11), (101.5, 11), (101.5, 42), (98.4, 42)], ls=":", color=C["dim"])
ax.text(102.6, 26, "--backend ollama", rotation=90, ha="center", va="center", fontsize=7.8,
        color=C["mute"])
# direct API calls from doctor/perf (bypass the agent)
path([(50, 65.4), (50, 67.6), (118, 67.6), (118, 65.4)], ls="--", color="#a78bfa")
label(84, 67.6, "doctor: GET /models  ·  perf: streamed /chat/completions (bypasses agent)")

fig.savefig(OUT, dpi=DPI, facecolor="white")
print(OUT)
