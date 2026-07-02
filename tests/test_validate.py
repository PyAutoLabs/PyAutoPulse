"""tests/test_validate.py — release-validation artifact ingest logic."""

from __future__ import annotations

import importlib
import json

import pytest

from heart import validate


def _write(path, payload):
    path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload)
    return path


REHEARSAL = {
    "mode": "rehearsal",
    "index": "testpypi",
    "version": "2026.6.30.1.dev64501",
    "packages": ["autoconf", "autoarray", "autofit", "autogalaxy", "autolens"],
    "run_id": "645",
    "run_attempt": "1",
    "build_sha": "abc1234def5678",
}

SHAS = {
    "PyAutoConf": "1" * 40,
    "PyAutoFit": "2" * 40,
    "PyAutoArray": "3" * 40,
    "PyAutoGalaxy": "4" * 40,
    "PyAutoLens": "5" * 40,
}

INTEGRATE = {
    "stage": "integrate",
    "status": "pass",
    "profile": "release",
    "run_url": "https://github.com/x/actions/runs/999",
    "commit_shas": SHAS,
    "summary": {"passed": 120, "failed": 0, "skipped": 3, "timeout": 0},
    "per_project": {
        "autolens_workspace": {"passed": 60, "failed": 0, "skipped": 1, "timeout": 0},
        "autolens_workspace_test": {"passed": 60, "failed": 0, "skipped": 2, "timeout": 0},
    },
    "failures": [],
}


# --- ingest: rehearsal only -------------------------------------------------


def test_ingest_rehearsal_only(tmp_path):
    _write(tmp_path / "rehearsal.json", REHEARSAL)
    report = validate.ingest([tmp_path])
    assert report["schema_version"] == validate.SCHEMA_VERSION
    assert report["testpypi_version"] == "2026.6.30.1.dev64501"
    assert report["stages"]["rehearse"]["status"] == "pass"
    assert report["stages"]["rehearse"]["run_id"] == "645"
    # rehearsal artifact presence = build succeeded → release_ready True (pass axis)
    assert report["release_ready"] is True
    # no integration stage yet → no release profile (the gate keeps this YELLOW)
    assert report["profile"] is None
    # the build sha is recorded under PyAutoBuild, not a library head
    assert report["commit_shas"].get("PyAutoBuild") == "abc1234def5678"


def test_ingest_version_txt_fallback(tmp_path):
    _write(tmp_path / "testpypi_version.txt", "2026.7.1.1.dev70101\n")
    report = validate.ingest([tmp_path])
    assert report["testpypi_version"] == "2026.7.1.1.dev70101"


# --- ingest: full pipeline --------------------------------------------------


def test_ingest_full_pass(tmp_path):
    _write(tmp_path / "rehearsal.json", REHEARSAL)
    _write(tmp_path / "commit_shas.json", SHAS)
    _write(tmp_path / "integrate.json", INTEGRATE)
    report = validate.ingest([tmp_path])
    assert report["release_ready"] is True
    assert report["profile"] == "release"
    assert report["commit_shas"]["PyAutoLens"] == "5" * 40
    assert report["totals"] == {"passed": 120, "failed": 0, "skipped": 3, "timeout": 0}
    assert report["per_project"]["autolens_workspace"]["passed"] == 60
    assert report["run_urls"]["integrate"].endswith("/999")
    assert report["stages"]["integrate"]["status"] == "pass"


def test_ingest_commit_shas_wrapper_form(tmp_path):
    _write(tmp_path / "rehearsal.json", REHEARSAL)
    _write(tmp_path / "commit_shas.json", {"commit_shas": SHAS})
    report = validate.ingest([tmp_path])
    assert report["commit_shas"]["PyAutoFit"] == "2" * 40


# --- ingest: failure axis ---------------------------------------------------


def test_ingest_failed_stage_is_not_ready(tmp_path):
    _write(tmp_path / "rehearsal.json", REHEARSAL)
    bad = dict(INTEGRATE, status="failure",
               summary={"passed": 100, "failed": 5, "skipped": 0, "timeout": 1},
               failures=[{"project": "autolens_workspace", "script": "x.py",
                          "log_url": "http://logs/1"}])
    _write(tmp_path / "integrate.json", bad)
    report = validate.ingest([tmp_path])
    assert report["release_ready"] is False
    assert report["stages"]["integrate"]["status"] == "fail"
    assert report["totals"]["failed"] == 5
    assert report["failures"][0]["script"] == "x.py"


def test_ingest_nothing_is_not_ready(tmp_path):
    # empty dir → no rehearse stage → not release_ready (nothing was built)
    report = validate.ingest([tmp_path])
    assert report["release_ready"] is False
    assert report["stages"] == {}


# --- ingest: explicit overrides ---------------------------------------------


def test_ingest_explicit_overrides(tmp_path):
    _write(tmp_path / "rehearsal.json", REHEARSAL)
    report = validate.ingest(
        [tmp_path],
        profile="release",
        testpypi_version="9.9.9",
        commit_shas=SHAS,
    )
    assert report["profile"] == "release"
    assert report["testpypi_version"] == "9.9.9"
    assert report["commit_shas"]["PyAutoConf"] == "1" * 40


def test_ingest_explicit_file_path_not_dir(tmp_path):
    p = _write(tmp_path / "rehearsal.json", REHEARSAL)
    report = validate.ingest([str(p)])
    assert report["stages"]["rehearse"]["status"] == "pass"


# --- helpers ----------------------------------------------------------------


@pytest.mark.parametrize(
    "token,expected",
    [
        ("pass", "pass"), ("success", "pass"), ("passed", "pass"),
        ("failure", "fail"), ("failed", "fail"), ("timed_out", "fail"),
        ("skipped", "skip"), ("", "skip"), ("weird", "skip"),
    ],
)
def test_norm_status(token, expected):
    assert validate._norm_status(token) == expected


def test_classify(tmp_path):
    assert validate._classify("rehearsal.json", REHEARSAL) == "rehearsal"
    assert validate._classify("x.json", INTEGRATE) == "stage"
    assert validate._classify("commit_shas.json", SHAS) == "commit_shas"
    assert validate._classify("x.json", {"commit_shas": SHAS}) == "commit_shas"
    assert validate._classify("x.json", [1, 2]) == "unknown"


# --- run(): persistence -----------------------------------------------------


def test_run_persists_report_and_history(tmp_path, monkeypatch):
    monkeypatch.setenv("HEART_STATE_DIR", str(tmp_path))
    import heart.state as state_mod
    importlib.reload(state_mod)
    import heart.validate as v_mod
    importlib.reload(v_mod)

    src = tmp_path / "artifacts"
    src.mkdir()
    _write(src / "rehearsal.json", REHEARSAL)
    _write(src / "commit_shas.json", SHAS)
    _write(src / "integrate.json", INTEGRATE)

    report = v_mod.run([src])
    out = tmp_path / "validation_report.json"
    assert out.is_file()
    assert json.loads(out.read_text())["release_ready"] is True
    # no leftover temp files (atomic writes)
    assert [p for p in tmp_path.iterdir() if ".tmp" in p.name] == []
    # a history archive copy exists
    hist = list((tmp_path / "validation_history").glob("*.json"))
    assert len(hist) == 1
    assert json.loads(hist[0].read_text())["testpypi_version"] == report["testpypi_version"]

    # load() round-trips
    assert v_mod.load()["profile"] == "release"

    importlib.reload(state_mod)
    importlib.reload(v_mod)


def test_run_out_override(tmp_path, monkeypatch):
    monkeypatch.setenv("HEART_STATE_DIR", str(tmp_path))
    import heart.state as state_mod
    importlib.reload(state_mod)
    import heart.validate as v_mod
    importlib.reload(v_mod)

    _write(tmp_path / "rehearsal.json", REHEARSAL)
    custom = tmp_path / "custom.json"
    v_mod.run([tmp_path / "rehearsal.json"], out=custom)
    assert custom.is_file()

    importlib.reload(state_mod)
    importlib.reload(v_mod)
