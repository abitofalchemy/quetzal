"""Performance logging: backend latency/throughput + end-to-end Hermes turn + system snapshot."""
from __future__ import annotations

import csv
import json
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import psutil

from .profiles import ROOT, Profile

RESULTS = ROOT / "perf" / "results"
PROMPT = "List three prime numbers greater than 100, comma-separated, nothing else."
AGENT_PROMPT = "Use the terminal tool to run `uname -s` and reply with only its output."
FIELDS = ["ts", "host", "target", "backend", "model", "kind", "ok", "ttft_s", "total_s",
          "completion_tokens", "tok_per_s", "peak_rss_mb", "cpu_pct", "ram_used_mb",
          "ram_avail_mb", "gpu_mem_used_mb", "error"]


def system_snapshot() -> dict:
    vm = psutil.virtual_memory()
    snap = {"cpu_pct": psutil.cpu_percent(interval=0.2),
            "ram_used_mb": round((vm.total - vm.available) / 2**20),
            "ram_avail_mb": round(vm.available / 2**20), "gpu_mem_used_mb": ""}
    if shutil.which("nvidia-smi"):
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            snap["gpu_mem_used_mb"] = r.stdout.strip().splitlines()[0]
    return snap


def bench_backend(p: Profile, api_key: str, max_tokens: int = 64) -> dict:
    """One streamed chat completion straight to the backend (no agent)."""
    headers = {"Authorization": f"Bearer {api_key or 'no-key'}"}
    body = {"model": p.model, "stream": True, "max_tokens": max_tokens, "temperature": 0,
            "stream_options": {"include_usage": True},
            "messages": [{"role": "user", "content": PROMPT}]}
    t0 = time.perf_counter()
    ttft, tokens, chunks = None, None, 0
    with httpx.stream("POST", f"{p.base_url}/chat/completions", json=body,
                      headers=headers, timeout=120) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            ev = json.loads(line[6:])
            if ev.get("choices") and ev["choices"][0].get("delta", {}).get("content"):
                chunks += 1
                ttft = ttft or time.perf_counter() - t0
            if ev.get("usage"):
                tokens = ev["usage"].get("completion_tokens")
    total = time.perf_counter() - t0
    tokens = tokens or chunks
    gen = total - (ttft or 0)
    return {"ok": True, "ttft_s": round(ttft or 0, 3), "total_s": round(total, 3),
            "completion_tokens": tokens, "tok_per_s": round(tokens / gen, 1) if gen > 0 else ""}


def bench_agent(env: dict) -> dict:
    """One non-interactive Hermes turn using the terminal tool; tracks peak RSS of the process tree."""
    cmd = ["hermes", "chat", "-Q", "-q", AGENT_PROMPT]
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    ps, peak = psutil.Process(proc.pid), 0
    while proc.poll() is None:
        try:
            rss = ps.memory_info().rss + sum(c.memory_info().rss for c in ps.children(recursive=True))
            peak = max(peak, rss)
        except psutil.Error:
            pass
        time.sleep(0.1)
    out = proc.stdout.read()
    total = time.perf_counter() - t0
    ok = proc.returncode == 0 and platform.system() in out
    return {"ok": ok, "total_s": round(total, 2), "peak_rss_mb": round(peak / 2**20),
            "error": "" if ok else out.strip()[-200:].replace("\n", " ")}


def log_row(p: Profile, kind: str, result: dict) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / f"{p.target}.csv"
    row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "host": platform.node(), "target": p.target, "backend": p.backend,
           "model": p.model, "kind": kind, **system_snapshot(), **result}
    new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)
    return path


def run(p: Profile, env: dict, runs: int = 3, agent: bool = True) -> list[dict]:
    rows = []
    key = env.get(p.api_key_env, "") if p.api_key_env else ""
    for _ in range(runs):
        try:
            res = bench_backend(p, key)
        except Exception as e:  # log failures too; they are data
            res = {"ok": False, "error": f"{type(e).__name__}: {e}".splitlines()[0][:200]}
        log_row(p, "backend", res)
        rows.append({"kind": "backend", **res})
    if agent:
        res = bench_agent(env)
        log_row(p, "agent", res)
        rows.append({"kind": "agent", **res})
    return rows
