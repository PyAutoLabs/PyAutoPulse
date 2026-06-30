"""heart/checks/ci_status.py — per-required-workflow CI conclusions on main HEAD.

The bash entry point (``ci_status.sh``) fetches, per polled repo, the recent
workflow runs on ``main`` plus the ``main`` HEAD sha via ``gh``, then pipes the
runs JSON here. This module owns the *logic*: pick the latest run of each
workflow on main, roll the **required** workflows for the repo's group into a
single conclusion, write the structured sidecar, and print the coloured summary
line. Keeping it in Python (not inlined ``python3 -c`` in bash) makes the
gating logic unit-testable in isolation.

Why per-workflow, not "the newest run": each workspace gates on several
workflows (e.g. ``Smoke Tests`` + ``Navigator Check``), each a matrix over two
Pythons. ``gh run list --limit 1`` returns one run of *some* workflow, so it can
report a green ``Navigator Check`` while ``Smoke Tests`` was red, or a run from a
feature branch. For release readiness we need the conclusion of **each required
workflow on the ``main`` HEAD commit**.

Sidecar schema written to ``<name>.ci_status.json``::

    {
      "name": "autolens_workspace",
      "group": "workspaces",
      "head_sha": "abc1234",
      "required": ["Smoke Tests", "Navigator Check"],
      "conclusion": "failure",        # rolled-up over required workflows (back-compat)
      "status": "completed",          # rolled-up status (back-compat)
      "sha": "abc1234",               # short HEAD sha (back-compat with old sidecar)
      "workflow": "Smoke Tests",      # the failing/representative workflow, for the summary
      "url": "https://github.com/.../actions/runs/123",
      "workflows": {
        "Smoke Tests":     {"conclusion": "failure", "status": "completed",
                            "head_sha": "abc1234", "on_head": true, "url": "...",
                            "created_at": "..."},
        "Navigator Check": {"conclusion": "success", ...}
      },
      "ts": "..."
    }

The top-level ``conclusion``/``status``/``group``/``sha`` keys are retained so
the existing ``status.py`` repo glyph and the ``readiness`` library loop keep
working unchanged; the new ``workflows`` dict is the structured detail the
workspace-CI readiness gate consumes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HEART_HOME = Path(__file__).resolve().parents[2]
CONFIG_PATH = HEART_HOME / "config" / "repos.yaml"

# Conclusions that count as a hard failure for gating. Deliberately a denylist
# of genuine failures rather than "anything != success": ``skipped`` /
# ``neutral`` / ``stale`` are non-events (e.g. a path-filtered job) and must not
# RED a release. Mirrored in readiness.py.
FAILURE_CONCLUSIONS = frozenset(
    {"failure", "timed_out", "startup_failure", "cancelled", "action_required"}
)

# Fallback if config/repos.yaml is unreadable; kept in sync with the YAML.
DEFAULT_REQUIRED_WORKFLOWS: dict[str, list[str]] = {
    "libraries": ["Tests"],
    "workspaces": ["Smoke Tests", "Navigator Check"],
    "workspaces_test": ["Smoke Tests"],
    "howto": ["Smoke Tests", "Navigator Check"],
}


def load_required_workflows(config_path: Path | str = CONFIG_PATH) -> dict[str, list[str]]:
    """Return the group→required-workflows map from repos.yaml, or the default."""
    try:
        import yaml

        cfg = yaml.safe_load(Path(config_path).read_text()) or {}
        rw = cfg.get("required_workflows")
        if isinstance(rw, dict) and rw:
            return {str(k): list(v) for k, v in rw.items() if isinstance(v, list)}
    except Exception:
        pass
    return dict(DEFAULT_REQUIRED_WORKFLOWS)


def required_for(group: str, config_path: Path | str = CONFIG_PATH) -> list[str]:
    """Required gating workflows for ``group`` ([] if the group is advisory)."""
    return load_required_workflows(config_path).get(group, [])


def latest_per_workflow(runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Collapse ``gh run list`` output to the newest run of each workflow on main.

    Runs are expected already filtered to ``--branch main`` by the caller, but we
    also drop ``pull_request`` events defensively (a PR targeting main has
    headBranch == its source branch, so it normally won't appear, but be safe).
    Keyed by ``workflowName``; the value keeps the fields readiness/status need.
    """
    latest: dict[str, dict[str, Any]] = {}
    for run in runs or []:
        if not isinstance(run, dict):
            continue
        if run.get("event") == "pull_request":
            continue
        wf = run.get("workflowName") or run.get("name")
        if not wf:
            continue
        created = run.get("createdAt") or ""
        prev = latest.get(wf)
        if prev is None or created >= (prev.get("createdAt") or ""):
            latest[wf] = run
    return latest


def _wf_entry(run: dict[str, Any], head_sha: str) -> dict[str, Any]:
    run_sha = run.get("headSha") or ""
    return {
        "conclusion": run.get("conclusion") or "",
        "status": run.get("status") or "",
        "head_sha": run_sha[:7],
        "on_head": bool(head_sha) and run_sha == head_sha,
        "url": run.get("url") or "",
        "created_at": run.get("createdAt") or "",
    }


def rollup(workflows: dict[str, dict[str, Any]], required: list[str]) -> dict[str, str]:
    """Roll required-workflow conclusions into one (conclusion, status, workflow).

    - Any required workflow with a FAILURE_CONCLUSIONS conclusion → ``failure``
      (status ``completed``); ``workflow`` names the first such workflow so the
      summary can point at it.
    - All required present, completed, success **and on HEAD** → ``success``.
    - Otherwise (in-progress, queued, missing, or success on a stale sha) →
      conclusion ``""`` with status ``in_progress`` (an *unknown*, never a green).

    When ``required`` is empty (an advisory group) the caller passes the whole
    latest-per-workflow set as ``workflows`` and we report the single newest
    run's conclusion, preserving the old "latest run" dashboard signal.
    """
    if not required:
        # Advisory group: report the newest run across all workflows.
        newest = max(
            workflows.values(),
            key=lambda e: e.get("created_at", ""),
            default=None,
        )
        if newest is None:
            return {"conclusion": "", "status": "", "workflow": ""}
        return {
            "conclusion": newest.get("conclusion", ""),
            "status": newest.get("status", ""),
            "workflow": "",
        }

    failing = [wf for wf in required
               if (workflows.get(wf, {}).get("conclusion") in FAILURE_CONCLUSIONS)]
    if failing:
        return {"conclusion": "failure", "status": "completed", "workflow": failing[0]}

    all_green = all(
        workflows.get(wf, {}).get("conclusion") == "success"
        and workflows.get(wf, {}).get("status") in ("completed", "")
        and workflows.get(wf, {}).get("on_head", False)
        for wf in required
    )
    if all_green:
        return {"conclusion": "success", "status": "completed", "workflow": ""}

    return {"conclusion": "", "status": "in_progress", "workflow": ""}


def build_sidecar(
    name: str,
    group: str,
    runs: list[dict[str, Any]],
    head_sha: str,
    ts: str,
    config_path: Path | str = CONFIG_PATH,
) -> dict[str, Any]:
    """Construct the full ci_status sidecar dict for one repo."""
    required = required_for(group, config_path)
    latest = latest_per_workflow(runs)
    workflows = {wf: _wf_entry(run, head_sha) for wf, run in latest.items()}

    roll = rollup(workflows, required)
    # Pick a representative url: the failing workflow's, else HEAD's newest.
    rep_wf = roll["workflow"]
    rep = workflows.get(rep_wf) if rep_wf else None
    if rep is None:
        rep = max(workflows.values(), key=lambda e: e.get("created_at", ""), default=None)

    return {
        "name": name,
        "group": group,
        "head_sha": head_sha,
        "sha": (head_sha or "")[:7],
        "required": required,
        "conclusion": roll["conclusion"],
        "status": roll["status"],
        "workflow": roll["workflow"],
        "url": (rep or {}).get("url", ""),
        "workflows": workflows,
        "ts": ts,
    }


def summary_line(sidecar: dict[str, Any]) -> str:
    """Coloured one-line summary for the daemon log."""
    from heart.heart_color import (
        c_fail, c_info, c_meta, c_ok, c_warn,
        glyph_fail, glyph_ok, glyph_warn,
    )

    name = sidecar.get("name", "?")
    conclusion = sidecar.get("conclusion", "")
    status = sidecar.get("status", "")
    sha = sidecar.get("sha", "")
    workflows = sidecar.get("workflows") or {}

    if not workflows and not sha:
        return f"{c_meta('·')} {c_info(name)} {c_meta('(no runs)')}"
    if conclusion == "success":
        return f"{glyph_ok()} {c_info(name)} {c_ok('success')} {c_meta(f'({sha})')}"
    if conclusion == "failure":
        wf = sidecar.get("workflow") or "?"
        return f"{glyph_fail()} {c_info(name)} {c_fail('FAILURE')} {c_meta(f'{wf} @ {sha}')}"
    # unknown / in-progress
    detail = status or "pending"
    return f"{glyph_warn()} {c_info(name)} {c_warn(detail)} {c_meta(f'({sha})')}"


def write_and_summarise(
    name: str,
    group: str,
    runs: list[dict[str, Any]],
    head_sha: str,
    ts: str,
    out_path: Path,
    config_path: Path | str = CONFIG_PATH,
) -> dict[str, Any]:
    sidecar = build_sidecar(name, group, runs, head_sha, ts, config_path)
    sys.path.insert(0, str(HEART_HOME))
    from heart import state

    state.atomic_write_json(out_path, sidecar)
    return sidecar


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="heart.checks.ci_status")
    ap.add_argument("--name", required=True)
    ap.add_argument("--group", required=True)
    ap.add_argument("--head-sha", default="")
    ap.add_argument("--ts", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)

    try:
        runs = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        runs = []
    if not isinstance(runs, list):
        runs = []

    sidecar = write_and_summarise(
        ns.name, ns.group, runs, ns.head_sha, ns.ts, Path(ns.out)
    )
    print(summary_line(sidecar))
    return 0


if __name__ == "__main__":
    sys.exit(main())
