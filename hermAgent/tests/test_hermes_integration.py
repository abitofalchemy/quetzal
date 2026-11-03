"""Checks against the installed Hermes itself (no model calls unless marked live)."""
import os
import subprocess

import pytest

from hermagent import cli, profiles


def hermes(p, *args):
    env = cli.build_env(p)
    return subprocess.run(["hermes", *args], env=env, capture_output=True, text=True, timeout=60)


@pytest.fixture(scope="module")
def p():
    prof = profiles.resolve("linux-dev")
    profiles.render(prof)
    return prof


def test_hermes_reads_rendered_model(p):
    r = hermes(p, "config", "get", "model")
    assert "qwen/qwen3-30b-a3b-instruct-2507" in r.stdout


def test_hermes_enables_only_allowed_toolsets(p):
    out = hermes(p, "tools", "list").stdout
    enabled = {ln.split()[2] for ln in out.splitlines() if "✓ enabled" in ln}
    assert enabled == {"file", "terminal"}


@pytest.mark.live
def test_live_agent_turn(p):
    env = cli.build_env(p)
    if not env.get(p.api_key_env):
        pytest.skip(f"{p.api_key_env} not set")
    r = subprocess.run(["hermes", "chat", "-Q", "-q", "Reply with exactly: PONG"],
                       env=env, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0 and "PONG" in r.stdout
