import yaml
import pytest

from hermagent import profiles

CFG = profiles.load()


@pytest.mark.parametrize("system,machine,want", [
    ("Linux", "x86_64", "linux-dev"),
    ("Darwin", "arm64", "mac-m4"),
])
def test_detect_target(system, machine, want):
    assert profiles.detect_target(CFG, system, machine) == want


def test_unknown_platform_exits():
    with pytest.raises(SystemExit):
        profiles.detect_target(CFG, "Windows", "AMD64")


@pytest.mark.parametrize("target", ["linux-dev", "mac-m4"])
def test_default_backend_is_openrouter(target):
    p = profiles.resolve(target)
    assert (p.backend, p.provider, p.model) == ("openrouter", "openrouter", "qwen/qwen3-30b-a3b-instruct-2507")


def test_backend_override_to_ollama():
    p = profiles.resolve("mac-m4", "ollama")
    c = profiles.hermes_config(p)["model"]
    assert c["provider"] == "custom" and c["base_url"] == "http://localhost:11434/v1"
    assert c["default"] == "qwen3:4b-instruct-2507"
    assert c["ollama_num_ctx"] == c["context_length"] >= 64_000


def test_unknown_backend_exits():
    with pytest.raises(SystemExit):
        profiles.resolve("linux-dev", "nope")


def test_context_meets_hermes_minimum():
    from agent.model_metadata import MINIMUM_CONTEXT_LENGTH
    assert CFG["context_length"] >= MINIMUM_CONTEXT_LENGTH


def test_minimal_toolsets_and_manual_approval():
    c = profiles.hermes_config(profiles.resolve("linux-dev"))
    assert c["toolsets"] == ["file", "terminal"]
    assert c["platform_toolsets"]["cli"] == ["file", "terminal"]
    assert c["approvals"]["mode"] == "manual" and c["approvals"]["cron_mode"] == "deny"


def test_render_writes_valid_yaml(tmp_path):
    out = profiles.render(profiles.resolve("linux-dev"), home=tmp_path)
    assert yaml.safe_load(out.read_text())["model"]["provider"] == "openrouter"


def test_hermes_version_pinned():
    from importlib.metadata import version
    assert version("hermes-agent") == CFG["hermes_version"]
