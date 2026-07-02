"""heart/validate.py — ingest release-validation artifacts into one report.

This is the **M2 foundation** of the Brain→Health→Heart release-validation
redesign. It owns two things and nothing else:

1. The **schema** of ``validation_report.json`` — the tracked artifact that
   answers *"was the exact source about to ship built, published to TestPyPI,
   installed from the wheel, and exercised at release fidelity — and did it
   pass?"*.
2. ``pyauto-heart validate --ingest <artifacts...>`` — **ingest-and-judge
   only**. It consumes the artifacts/conclusions the Brain Release Agent has
   already collected (the M1 TestPyPI rehearsal artifact, and — from M3 — the
   wheel-based integration ``report.json``), assembles the single
   ``validation_report.json``, computes ``release_ready``, persists it in Heart
   state, and archives a history copy.

**Boundary (non-negotiable, mirrors CLAUDE.md).** This module NEVER dispatches
a build, never talks to GitHub, never mutates any repo. All dispatching / polling
/ artifact download is the Brain Release Agent's job; Heart is spec + ingest +
verdict, credential-free. It writes ONLY under ``~/.pyauto-heart/``.

Schema of ``validation_report.json`` (``schema_version`` 1)::

    {
      "schema_version": 1,
      "release_ready": true,            # top-level pass/fail axis (no stage failed)
      "testpypi_version": "2026.6.30.1.dev64501",
      "profile": "release",             # env profile the integration tier ran under
      "commit_shas": {                  # per-repo HEAD the rehearsal was built from
        "PyAutoConf": "abc123...", "PyAutoFit": "...", "PyAutoArray": "...",
        "PyAutoGalaxy": "...", "PyAutoLens": "..."
      },
      "stages": {                       # per-stage status (pass|fail|skip)
        "unit":      {"status": "pass", "run_url": "..."},
        "rehearse":  {"status": "pass", "index": "testpypi", "version": "...",
                      "run_id": "645", "build_sha": "...", "packages": [...]},
        "integrate": {"status": "pass", "profile": "release", "run_url": "..."}
      },
      "totals": {"passed": N, "failed": N, "skipped": N, "timeout": N},
      "per_project": {                  # per-workspace pass/fail/skip/timeout
        "autolens_workspace":      {"passed": .., "failed": .., ...},
        "autolens_workspace_test": {"passed": .., "failed": .., ...}
      },
      "failures": [                     # failing entries, with logs / run URLs
        {"project": "...", "script": "...", "log_url": "..."}
      ],
      "run_urls": {"rehearse": "...", "integrate": "..."},
      "ts": "2026-06-30T12:00:00+00:00"
    }

``release_ready`` is the **pass/fail** axis only: it is ``false`` if any ran
stage failed. Release *fidelity* and *freshness* (``profile == release``,
``commit_shas`` matching the current ``main`` HEADs, age) are judged separately
by the readiness gate (``heart/readiness.py``) — a passing-but-stale or
passing-but-wrong-profile report is YELLOW there, not GREEN, while a failing one
is RED. Keeping the axes separate is what lets an M2 rehearsal-only report be
faithfully ``release_ready`` yet still gate YELLOW until M3 wires the
release-fidelity integration.

Recognised input artifacts (files, or directories scanned for them):

- ``rehearsal.json`` / ``testpypi_version.txt`` — the M1 rehearsal artifact
  (``testpypi-rehearsal-version``). Its presence means all five wheels built,
  uploaded, and installed, so the ``rehearse`` stage is ``pass``.
- ``commit_shas.json`` — ``{repo: sha}`` (or ``{"commit_shas": {...}}``), the
  HEADs the Release Agent built from (it has the GitHub access to read them).
- a **stage report** — any JSON carrying a ``stage`` key (``unit`` /
  ``integrate`` from M3's ``workspace-validation.yml``): ``status``, ``profile``,
  ``summary``, ``per_project``, ``failures``, ``run_url``, ``commit_shas``.
- a full ``validation_report.json`` — merged as a base (idempotent re-ingest).
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

from heart import state

SCHEMA_VERSION = 1

VALIDATION_REPORT_FILE = state.HEART_STATE_DIR / "validation_report.json"
VALIDATION_HISTORY_DIR = state.HEART_STATE_DIR / "validation_history"

_COUNT_KEYS = ("passed", "failed", "skipped", "timeout")


def _now_iso(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return now.isoformat()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _norm_status(value: Any) -> str:
    """Map a stage/status token onto pass|fail|skip (unknown → ``skip``)."""
    s = str(value or "").strip().lower()
    if s in ("pass", "passed", "success", "succeeded", "ok", "green", "true"):
        return "pass"
    if s in ("fail", "failed", "failure", "timed_out", "timeout", "error", "red", "false"):
        return "fail"
    if s in ("skip", "skipped", "neutral", "cancelled", "canceled"):
        return "skip"
    return "skip"


def _iter_source_files(sources: Iterable[str | Path]) -> list[Path]:
    """Expand each source (file or dir) into concrete artifact file paths.

    Directories are scanned (one level, then recursively) for the known JSON
    filenames plus ``*version*.txt``; explicit file paths are used verbatim.
    Order is preserved and de-duplicated so a later, more-specific artifact can
    override an earlier one deterministically.
    """
    seen: set[Path] = set()
    out: list[Path] = []

    def _add(p: Path) -> None:
        rp = p.resolve()
        if rp not in seen and p.is_file():
            seen.add(rp)
            out.append(p)

    for src in sources:
        p = Path(src)
        if p.is_dir():
            # Scan every JSON (unknown kinds are ignored by _classify) plus any
            # version text file, so a directory of downloaded artifacts is picked
            # up whatever the stage report is named (rehearsal.json,
            # integrate.json, report.json, commit_shas.json, ...).
            for hit in sorted(p.rglob("*.json")):
                _add(hit)
            for txt in sorted(p.rglob("*version*.txt")):
                _add(txt)
        else:
            _add(p)
    return out


def _classify(name: str, data: Any) -> str:
    """Return the artifact kind for a loaded JSON body / filename."""
    if not isinstance(data, dict):
        return "unknown"
    if "release_ready" in data and "stages" in data:
        return "report"
    if data.get("mode") == "rehearsal" or data.get("index") == "testpypi":
        return "rehearsal"
    if "packages" in data and "version" in data:
        return "rehearsal"
    if "stage" in data:
        return "stage"
    if "commit_shas" in data:
        return "commit_shas"
    if name == "commit_shas.json":
        return "commit_shas"
    return "unknown"


class _Accumulator:
    """Mutable fold state while merging artifacts, distilled into a report."""

    def __init__(self) -> None:
        self.testpypi_version: str | None = None
        self.profile: str | None = None
        self.commit_shas: dict[str, str] = {}
        self.stages: dict[str, dict[str, Any]] = {}
        self.totals: dict[str, int] = {k: 0 for k in _COUNT_KEYS}
        self.per_project: dict[str, dict[str, int]] = {}
        self.failures: list[dict[str, Any]] = []
        self.run_urls: dict[str, str] = {}
        self._explicit_ready: bool | None = None

    def _add_counts(self, target: dict[str, int], summary: dict[str, Any]) -> None:
        for k in _COUNT_KEYS:
            v = summary.get(k)
            if isinstance(v, (int, float)):
                target[k] += int(v)

    def _merge_per_project(self, per_project: dict[str, Any]) -> None:
        for proj, counts in (per_project or {}).items():
            if not isinstance(counts, dict):
                continue
            bucket = self.per_project.setdefault(proj, {k: 0 for k in _COUNT_KEYS})
            for k in _COUNT_KEYS:
                v = counts.get(k)
                if isinstance(v, (int, float)):
                    bucket[k] += int(v)

    def add_rehearsal(self, data: dict[str, Any]) -> None:
        version = data.get("version")
        if version and not self.testpypi_version:
            self.testpypi_version = str(version)
        stage = {
            "status": "pass",  # artifact presence == all 5 wheels built/installed
            "index": data.get("index", "testpypi"),
            "version": str(version) if version else self.testpypi_version,
        }
        for key in ("run_id", "run_attempt", "build_sha", "packages"):
            if data.get(key) is not None:
                stage[key] = data[key]
        self.stages["rehearse"] = stage
        if data.get("build_sha"):
            self.commit_shas.setdefault("PyAutoBuild", str(data["build_sha"]))

    def add_stage(self, data: dict[str, Any]) -> None:
        name = str(data.get("stage") or "").strip() or "stage"
        entry: dict[str, Any] = {"status": _norm_status(data.get("status"))}
        if data.get("profile"):
            entry["profile"] = str(data["profile"])
            self.profile = str(data["profile"])
        if data.get("run_url"):
            entry["run_url"] = str(data["run_url"])
            self.run_urls[name] = str(data["run_url"])
        if data.get("version") and not self.testpypi_version:
            self.testpypi_version = str(data["version"])
        self.stages[name] = entry

        summary = data.get("summary")
        if isinstance(summary, dict):
            self._add_counts(self.totals, summary)
        self._merge_per_project(data.get("per_project", {}) or {})
        for f in data.get("failures", []) or []:
            if isinstance(f, dict):
                self.failures.append(f)
        self.add_commit_shas(data.get("commit_shas"))

    def add_commit_shas(self, shas: Any) -> None:
        if not isinstance(shas, dict):
            return
        for repo, sha in shas.items():
            if sha:
                self.commit_shas[str(repo)] = str(sha)

    def add_report(self, data: dict[str, Any]) -> None:
        """Merge a previously-emitted full report as a base."""
        if data.get("testpypi_version") and not self.testpypi_version:
            self.testpypi_version = str(data["testpypi_version"])
        if data.get("profile") and not self.profile:
            self.profile = str(data["profile"])
        self.add_commit_shas(data.get("commit_shas"))
        for name, entry in (data.get("stages") or {}).items():
            if isinstance(entry, dict) and name not in self.stages:
                self.stages[name] = dict(entry)
        if isinstance(data.get("totals"), dict):
            self._add_counts(self.totals, data["totals"])
        self._merge_per_project(data.get("per_project", {}) or {})
        for f in data.get("failures", []) or []:
            if isinstance(f, dict):
                self.failures.append(f)
        for k, v in (data.get("run_urls") or {}).items():
            self.run_urls.setdefault(str(k), str(v))
        if isinstance(data.get("release_ready"), bool):
            self._explicit_ready = data["release_ready"]

    def release_ready(self) -> bool:
        """True iff no ran stage failed AND the rehearse stage passed.

        The rehearse stage is mandatory: a report with nothing built is not
        release-ready. An explicit ``release_ready`` from a merged base report is
        honoured only when no stage contradicts it with a failure.
        """
        if any(s.get("status") == "fail" for s in self.stages.values()):
            return False
        if self._explicit_ready is not None:
            return bool(self._explicit_ready)
        rehearse = self.stages.get("rehearse")
        return bool(rehearse and rehearse.get("status") == "pass")


def ingest(
    sources: Sequence[str | Path],
    *,
    profile: str | None = None,
    testpypi_version: str | None = None,
    commit_shas: dict[str, str] | None = None,
    now: datetime.datetime | None = None,
) -> dict[str, Any]:
    """Fold the given artifacts into a single ``validation_report`` dict.

    Pure (no I/O side effects beyond reading the source files); ``run`` persists
    the result. Explicit ``profile`` / ``testpypi_version`` / ``commit_shas``
    override / seed whatever the artifacts carry — the Release Agent uses these
    to inject the HEADs it built from.
    """
    acc = _Accumulator()
    if commit_shas:
        acc.add_commit_shas(commit_shas)

    for path in _iter_source_files(sources):
        if path.suffix == ".txt":
            if "version" in path.name.lower() and not acc.testpypi_version:
                txt = None
                try:
                    txt = path.read_text().strip()
                except OSError:
                    txt = None
                if txt:
                    acc.testpypi_version = txt.splitlines()[0].strip()
            continue
        data = _read_json(path)
        kind = _classify(path.name, data)
        if kind == "rehearsal":
            acc.add_rehearsal(data)
        elif kind == "stage":
            acc.add_stage(data)
        elif kind == "commit_shas":
            acc.add_commit_shas(data.get("commit_shas") if "commit_shas" in data else data)
        elif kind == "report":
            acc.add_report(data)
        # unknown → ignored

    # Explicit overrides take precedence (Release-Agent-supplied truth).
    if testpypi_version:
        acc.testpypi_version = testpypi_version
    if profile:
        acc.profile = profile

    return {
        "schema_version": SCHEMA_VERSION,
        "release_ready": acc.release_ready(),
        "testpypi_version": acc.testpypi_version,
        "profile": acc.profile,
        "commit_shas": dict(sorted(acc.commit_shas.items())),
        "stages": acc.stages,
        "totals": acc.totals,
        "per_project": acc.per_project,
        "failures": acc.failures,
        "run_urls": acc.run_urls,
        "ts": _now_iso(now),
    }


def _archive_name(report: dict[str, Any]) -> str:
    """A stable, sortable history filename for one ingested report."""
    ver = str(report.get("testpypi_version") or "unknown").replace("/", "_")
    ts = str(report.get("ts") or _now_iso()).replace(":", "").replace("/", "_")
    return f"{ts}__{ver}.json"


def run(
    sources: Sequence[str | Path],
    *,
    profile: str | None = None,
    testpypi_version: str | None = None,
    commit_shas: dict[str, str] | None = None,
    out: Path | None = None,
    now: datetime.datetime | None = None,
) -> dict[str, Any]:
    """Ingest, persist ``validation_report.json`` + a history copy, and return it.

    Persistence stays entirely inside ``~/.pyauto-heart/`` — the canonical report
    plus an append-only ``validation_history/`` archive so Heart tracks release
    health over time without ever mutating a source repo.
    """
    report = ingest(
        sources,
        profile=profile,
        testpypi_version=testpypi_version,
        commit_shas=commit_shas,
        now=now,
    )
    target = out or VALIDATION_REPORT_FILE
    state.atomic_write_json(target, report)
    try:
        state.atomic_write_json(VALIDATION_HISTORY_DIR / _archive_name(report), report)
    except OSError:
        pass  # history is best-effort; the canonical report is what matters
    return report


def load() -> dict[str, Any] | None:
    """Return the persisted ``validation_report.json`` (or None)."""
    return _read_json(VALIDATION_REPORT_FILE)


def _print_summary(report: dict[str, Any]) -> None:
    from heart.heart_color import (
        c_fail, c_info, c_meta, c_ok, c_warn, glyph_fail, glyph_ok, glyph_warn,
    )

    ready = report.get("release_ready")
    if ready is True:
        glyph, label = glyph_ok(), c_ok("release_ready")
    elif ready is False:
        glyph, label = glyph_fail(), c_fail("NOT release_ready")
    else:
        glyph, label = glyph_warn(), c_warn("release_ready unknown")
    t = report.get("totals", {}) or {}
    stages = ", ".join(f"{n}:{s.get('status', '?')}" for n, s in (report.get("stages") or {}).items())
    version = report.get("testpypi_version") or "?"
    prof = report.get("profile") or "?"
    print(f"{glyph} {c_info('validate')} {label} {c_meta(f'v{version}  profile={prof}')}")
    print(
        c_meta(
            f"  stages: {stages or 'none'}  "
            f"totals: {t.get('passed', 0)}p/{t.get('failed', 0)}f/"
            f"{t.get('skipped', 0)}s/{t.get('timeout', 0)}t"
        )
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="pyauto-heart validate",
        description="Ingest release-validation artifacts into validation_report.json "
        "(ingest-and-judge only — never dispatches a build).",
    )
    ap.add_argument(
        "--ingest", nargs="+", metavar="PATH", default=None,
        help="artifact files/directories to ingest (rehearsal.json, commit_shas.json, stage report.json, ...)",
    )
    ap.add_argument("--profile", default=None, help="override the env profile the integration tier ran under")
    ap.add_argument("--testpypi-version", default=None, help="override the rehearsed TestPyPI version")
    ap.add_argument("--commit-shas", default=None, metavar="FILE", help="JSON file of {repo: sha} HEADs built from")
    ap.add_argument("--out", default=None, help="write the report here instead of the default state path")
    ap.add_argument("--json", action="store_true", help="print the resulting report as JSON")
    ns = ap.parse_args(argv)

    commit_shas: dict[str, str] | None = None
    if ns.commit_shas:
        data = _read_json(Path(ns.commit_shas))
        if isinstance(data, dict):
            commit_shas = data.get("commit_shas") if "commit_shas" in data else data

    if ns.ingest is None:
        report = load()
        if report is None:
            print("validate: no validation_report.json yet (run with --ingest <artifacts>)", file=sys.stderr)
            return 1
    else:
        report = run(
            ns.ingest,
            profile=ns.profile,
            testpypi_version=ns.testpypi_version,
            commit_shas=commit_shas,
            out=Path(ns.out) if ns.out else None,
        )

    if ns.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
