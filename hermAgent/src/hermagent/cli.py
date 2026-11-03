"""hagent — render config and run Hermes for a (target, backend) pair.

  hagent [--target T] [--backend B] render     write .hermes-home/config.yaml
  hagent [--target T] [--backend B] doctor     check key, backend reachability, config
  hagent [--target T] [--backend B] chat [...] render, then exec `hermes chat ...`
  hagent [--target T] [--backend B] perf       log latency/throughput to perf/results/<target>.csv
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

import httpx
from dotenv import dotenv_values

from . import perf, profiles


def build_env(p: profiles.Profile) -> dict:
    env = dict(os.environ)
    env.update({k: v for k, v in dotenv_values(profiles.ROOT / ".env").items() if v})
    env["HERMES_HOME"] = str(profiles.HERMES_HOME)
    return env


def doctor(p: profiles.Profile, env: dict) -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("hermes on PATH", shutil.which("hermes", path=env.get("PATH")) is not None, ""))
    if p.api_key_env:
        checks.append((f"{p.api_key_env} set", bool(env.get(p.api_key_env)), "add it to .env"))
    try:
        key = env.get(p.api_key_env, "") if p.api_key_env else ""
        hdr = {"Authorization": f"Bearer {key}"} if key else {}
        r = httpx.get(f"{p.base_url}/models", headers=hdr, timeout=10)
        ids = {m["id"] for m in r.json().get("data", [])}
        checks.append((f"backend reachable ({p.base_url})", r.status_code == 200, f"HTTP {r.status_code}"))
        checks.append((f"model {p.model} available", p.model in ids,
                       "ollama pull " + p.model if p.backend == "ollama" else "check model id"))
    except Exception as e:
        checks.append((f"backend reachable ({p.base_url})", False, type(e).__name__))
    cfg = profiles.HERMES_HOME / "config.yaml"
    checks.append(("config rendered", cfg.exists(), "run `hagent render`"))
    for name, ok, hint in checks:
        print(f"{'✓' if ok else '✗'} {name}" + ("" if ok else f"  → {hint}"))
    return 0 if all(ok for _, ok, _ in checks) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hagent", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", help="linux-dev | mac-m4 (default: auto-detect)")
    ap.add_argument("--backend", help="openrouter | ollama (default: target's default)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render")
    sub.add_parser("doctor")
    pp = sub.add_parser("perf")
    pp.add_argument("--runs", type=int, default=3)
    pp.add_argument("--no-agent", action="store_true", help="skip the end-to-end Hermes turn")
    sub.add_parser("chat", add_help=False)
    args, rest = ap.parse_known_args(argv)

    p = profiles.resolve(args.target, args.backend)
    path = profiles.render(p)
    env = build_env(p)
    print(f"[hagent] target={p.target} backend={p.backend} model={p.model}", file=sys.stderr)

    if args.cmd == "render":
        print(path)
        return 0
    if args.cmd == "doctor":
        return doctor(p, env)
    if args.cmd == "perf":
        for row in perf.run(p, env, runs=args.runs, agent=not args.no_agent):
            print(row)
        print(f"logged → {perf.RESULTS / (p.target + '.csv')}")
        return 0
    # chat: hand the process over to hermes so the TUI owns the terminal
    os.execvpe("hermes", ["hermes", "chat", *rest], env)


if __name__ == "__main__":
    sys.exit(main())
