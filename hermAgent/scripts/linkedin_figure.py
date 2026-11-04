"""Render docs/linkedin-architecture.png: high-level architecture + tech stack for the LinkedIn post.

Run:  uv run --no-project --with matplotlib==3.10.0 python scripts/linkedin_figure.py
Perf numbers come from perf/results/linux-dev.csv.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "linkedin-architecture.png"
W, H, DPI = 12, 6.75, 150  # 16:9, 1800x1013 px

C = {"ink": "#1f2933", "mute": "#52606d", "line": "#7b8794", "bg": "#ffffff", "panel": "#f5f7fa",
     "cli": "#dbeafe", "cfg": "#fef3c7", "hermes": "#dcfce7", "cloud": "#ede9fe",
     "violet": "#7c3aed", "dim": "#9aa5b1", "ok": "#15803d"}

fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=C["bg"])
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 120); ax.set_ylim(0, 67.5); ax.axis("off")


def box(x, y, w, h, title, body="", fc="#fff", ec=None, ls="-", ts=11, bs=8.6, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
                                fc=fc, ec=ec or C["line"], lw=1.3, ls=ls, zorder=z))
    if title:
        ax.text(x + 1.1, y + h - 1.2, title, ha="left", va="top", fontsize=ts, weight="bold",
                color=C["ink"], zorder=z + 1)
    if body:
        ax.text(x + 1.1, y + h - 4.4, body, ha="left", va="top", fontsize=bs, color=C["mute"],
                linespacing=1.45, zorder=z + 1)


def arrow(a, b, ls="-", color=None, both=False, text="", dx=0, dy=1.6):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="<|-|>" if both else "-|>", mutation_scale=12,
                                 lw=1.5, ls=ls, color=color or C["line"], zorder=5))
    if text:
        ax.text((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy, text, ha="center", va="center",
                fontsize=8, color=C["ink"], zorder=6)


# ---- header
ax.text(2.5, 65, "A reproducible Hermes Agent: one config file, two machines",
        fontsize=17, weight="bold", color=C["ink"], va="top")
ax.text(2.5, 60.6, "Pinned versions · minimal tools · human approval · tests and perf logs from day one",
        fontsize=10, color=C["mute"], va="top")

# ---- architecture (left)
ax.text(2.5, 55.5, "ARCHITECTURE", fontsize=9, weight="bold", color=C["dim"])
box(2.5, 36, 16, 16.5, "profiles.toml", "single source\nof truth\n+ .env (API key)", fc=C["cfg"])
box(23, 36, 16, 16.5, "hagent CLI", "detects machine\npicks backend\nrenders config\nruns doctor / perf",
    fc=C["cli"])
box(43.5, 36, 22, 16.5, "Hermes Agent 0.19", "file + terminal tools only\nmanual approval per\nrisky command\nmemory · web · cron: off",
    fc=C["hermes"])
arrow((18.9, 44), (22.6, 44))
arrow((39.4, 44), (43.1, 44), text="exec")

box(43.5, 15, 22, 15, "OpenRouter (default)", "Qwen3-30B-A3B\n262K context · hosted", fc=C["cloud"])
box(43.5, 2.5, 22, 9.5, "Ollama (optional)", "Qwen3-4B · local · 64K ctx", ls=":", ts=10, bs=8.2)
arrow((54.5, 35.6), (54.5, 30.4), both=True, color=C["violet"], text="HTTPS", dx=4.2, dy=0)
ax.plot([65.9, 67.8, 67.8], [40, 40, 7], ls=":", color=C["dim"], lw=1.5, zorder=4)
arrow((67.8, 7), (65.9, 7), ls=":", color=C["dim"])

# machines
ax.text(2.5, 30, "TARGETS  (--target, auto-detected)", fontsize=9, weight="bold", color=C["dim"])
box(2.5, 17.5, 34.5, 9.5, "linux-dev  ✓ tested", "Laptop · RTX 4050 6 GB · 7.5 GB RAM", fc="#fff",
    ec=C["ok"], ts=10.5, bs=8.4)
box(2.5, 2.5, 34.5, 9.5, "mac-m4  → next", "Mac mini M4 Pro · 24 GB unified", ec=C["dim"],
    ls="--", ts=10.5, bs=8.4)

# ---- right panel: stack + numbers
box(70, 2.5, 47.5, 50, "", fc=C["panel"], ec="#e4e7eb", z=1)
ax.text(72, 49.5, "TECH STACK", fontsize=9, weight="bold", color=C["dim"])
stack = [("Runtime", "Python 3.12 · uv + uv.lock"), ("Agent", "hermes-agent==0.19.0 (pinned)"),
         ("Model", "OpenRouter Qwen3-30B-A3B"), ("Local", "Ollama Qwen3-4B (optional)"),
         ("Wrapper", "hagent CLI (render · doctor · perf)"), ("Tests", "pytest: offline + live"),
         ("Perf", "CSV per machine (TTFT, tok/s, RSS)")]
for i, (k, v) in enumerate(stack):
    y = 46 - i * 3.6
    ax.text(72, y, k, fontsize=9, weight="bold", color=C["ink"], va="top")
    ax.text(83, y, v, fontsize=9, color=C["mute"], va="top")

rows = list(csv.DictReader((ROOT / "perf/results/linux-dev.csv").open()))
be = [r for r in rows if r["kind"] == "backend" and r["ok"] == "True"]
ag = [r for r in rows if r["kind"] == "agent" and r["ok"] == "True"]
ttft = sorted(float(r["ttft_s"]) for r in be)
tps = sorted(float(r["tok_per_s"]) for r in be)
ax.text(72, 19.5, "LINUX BASELINE", fontsize=9, weight="bold", color=C["dim"])
stats = [(f"{ttft[len(ttft) // 2]:.1f}s", "median time\nto first token"),
         (f"{tps[len(tps) // 2]:.0f}", "median\ntokens / s"),
         (f"{float(ag[-1]['total_s']):.1f}s", "full agent turn\nwith tool call"),
         (f"{ag[-1]['peak_rss_mb']} MB", "agent peak\nmemory")]
for i, (v, k) in enumerate(stats):
    x = 72 + i * 11.4
    ax.text(x, 16.2, v, fontsize=15, weight="bold", color=C["ink"], va="top")
    ax.text(x, 11, k, fontsize=7.8, color=C["mute"], va="top", linespacing=1.3)
ax.text(72, 5, "✓ 13/13 offline tests   ✓ live agent turn   ✓ doctor 5/5", fontsize=8.6, color=C["ok"],
        weight="bold", va="center")

ax.text(117.5, 0.9, "github.com/abitofalchemy/quetzal", ha="right", fontsize=8, color=C["dim"])

fig.savefig(OUT, dpi=DPI, facecolor=C["bg"])
print(OUT)
