"""tests/test_repo_config.py — config/repos.yaml schema validity."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def config():
    here = Path(__file__).resolve().parents[1]
    return yaml.safe_load((here / "config" / "repos.yaml").read_text())


def test_repos_block_present(config):
    assert "repos" in config
    assert isinstance(config["repos"], dict)


def test_every_repo_has_owner_and_name(config):
    for group, entries in config["repos"].items():
        assert isinstance(entries, list), f"group {group} must be a list"
        for repo in entries:
            assert "name" in repo, f"missing name in group {group}: {repo}"
            assert "owner" in repo, f"missing owner in group {group}: {repo}"
            assert isinstance(repo["name"], str)
            assert isinstance(repo["owner"], str)


def test_no_duplicate_repo_names(config):
    seen = set()
    for entries in config["repos"].values():
        for repo in entries:
            assert repo["name"] not in seen, f"duplicate repo: {repo['name']}"
            seen.add(repo["name"])


def test_excluded_repos_block_present(config):
    assert "excluded" in config
    assert isinstance(config["excluded"], list)


def test_thresholds_have_expected_fields(config):
    thresholds = config["thresholds"]
    assert thresholds["script_timing"]["yellow_factor"] > 1.0
    assert thresholds["script_timing"]["red_factor"] > thresholds["script_timing"]["yellow_factor"]
    assert thresholds["script_timing"]["baseline_window"] >= 3


def test_22_repos_polled(config):
    """Sanity check the polled count — bumps need a deliberate update."""
    total = sum(len(v) for v in config["repos"].values())
    assert total == 22, f"expected 22 polled repos, got {total}"


def _all_names(config):
    return {r["name"] for entries in config["repos"].values() for r in entries}


def test_registry_renames_applied(config):
    names = _all_names(config)
    # PyAutoPrompt → PyAutoMind, PyAutoPaper → PyAutoMemory.
    assert "PyAutoMind" in names and "PyAutoPrompt" not in names
    assert "PyAutoMemory" in names and "PyAutoPaper" not in names
    # Stale names must not linger in the excluded list either.
    assert "PyAutoPaper" not in config.get("excluded", [])


def test_organism_repos_polled(config):
    names = _all_names(config)
    for repo in ("PyAutoBrain", "PyAutoHeart", "PyAutoMemory"):
        assert repo in names, f"organism repo {repo} not polled"


def test_required_workflows_block(config):
    rw = config["required_workflows"]
    assert isinstance(rw, dict)
    # Every gated group must reference real repo groups and list workflow names.
    for group, workflows in rw.items():
        assert group in config["repos"], f"required_workflows group {group} not in repos"
        assert isinstance(workflows, list) and workflows
        assert all(isinstance(w, str) for w in workflows)
    # The smoke gate must exist for the user-facing workspaces; url is NOT a
    # required workflow (advisory only).
    assert "Smoke Tests" in rw["workspaces"]
    assert "Navigator Check" in rw["workspaces"]
    for workflows in rw.values():
        assert not any("url" in w.lower() for w in workflows)
