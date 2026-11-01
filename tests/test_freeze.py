"""Frozen snapshots (``pulse/freeze.py``): the day-zero baseline captured once, never rewritten."""

import copy
import json
from types import SimpleNamespace

import pytest
from conftest import SHA_A, fixture_doc
from test_ingest import _decisions

from pulse import cli, freeze, ingest, summary

GH = "PyAutoLabs/autolens_profiling"
LENS = SimpleNamespace(
    instance="lens",
    repo="autolens_profiling",
    github=GH,
    summary_path="dashboard/catalogue.json",
)
TAG = "2026.10.16.2"


@pytest.fixture
def root(tmp_path):
    root = tmp_path / "organ"
    _decisions(root, ["fixture-designation"])
    return root


def _freeze(root, doc=None, label="day_zero"):
    doc = doc or fixture_doc("setup_summary_v3.json")
    raw = json.dumps(doc).encode()
    snap = freeze.build(LENS, doc, raw, SHA_A, label, "2026-11-01T00:00:00Z", root)
    return freeze.write(root, snap), snap


def test_freeze_keeps_only_the_stamped_records_with_a_manifest(root):
    path, snap = _freeze(root)
    assert path == root / "snapshots" / "day_zero" / "lens.json"
    assert snap["tag"] == TAG and snap["commit"] == SHA_A
    assert [r["id"] for r in snap["records"]] == ["imaging-delaunay-hst-a100-runtime"]
    assert snap["counts"] == {
        "records": 1,
        "cells": 1,
        "by_class": {"optimal": 1},
        "with_decision": 1,
    }
    assert snap["decision_ids"] == ["fixture-designation"]
    assert snap["source"]["record_count"] == 6 and len(snap["source"]["sha256"]) == 64
    assert snap["planned_cells"] == fixture_doc("setup_summary_v3.json").get("planned_cells", [])
    ok, problems = freeze.verify(root, root)
    assert problems == [] and ok[0].startswith("day_zero/lens: tag 2026.10.16.2, 1 records")


def test_a_frozen_snapshot_is_never_rewritten(root):
    _freeze(root)
    with pytest.raises(freeze.FreezeError, match="never rewritten"):
        _freeze(root)
    # A new baseline is a new label.
    path, _snap = _freeze(root, label="day_zero_2")
    assert path.parent.name == "day_zero_2"


def test_verify_catches_an_edited_record_and_an_unresolved_decision(root):
    path, _snap = _freeze(root)
    snap = json.loads(path.read_text())
    snap["records"][0]["values"] = {"single_call": 0.001}
    path.write_text(json.dumps(snap))
    _ok, problems = freeze.verify(root, root)
    assert any("records_sha256 mismatch" in p for p in problems)
    path.unlink()
    _freeze(root)
    (root / "decisions" / "fixture-designation.md").unlink()
    with pytest.raises(ValueError):
        freeze.verify(root, root)  # the decision index itself is now invalid
    _decisions(root, ["other"])
    _ok, problems = freeze.verify(root, root)
    assert any("not in decisions.yaml: fixture-designation" in p for p in problems)


def test_freeze_refuses_a_catalogue_with_no_or_two_day_zero_tags(root):
    doc = fixture_doc("setup_summary_v3.json")
    none = copy.deepcopy(doc)
    for record in none["records"]:
        record["day_zero"] = None
    with pytest.raises(freeze.FreezeError, match="exactly one day_zero tag"):
        _freeze(root, none)
    two = copy.deepcopy(doc)
    two["records"][2]["day_zero"] = "2026.10.25.1"
    with pytest.raises(freeze.FreezeError, match="exactly one day_zero tag"):
        _freeze(root, two)


def test_freeze_refuses_an_invalid_catalogue(root):
    _decisions(root, ["other"])
    with pytest.raises(freeze.FreezeError, match="invalid"):
        _freeze(root)


def test_only_a_current_record_carries_a_day_zero_stamp():
    doc = fixture_doc("setup_summary_v3.json")
    assert summary.classify(doc, ("profiling-summary", 3)) == ("ok", [])
    bad = copy.deepcopy(doc)
    [old] = [r for r in bad["records"] if r["status"] == "superseded"]
    old["day_zero"] = TAG
    outcome, errors = summary.classify(bad, ("profiling-summary", 3))
    assert outcome == "invalid"
    assert any("only a current record carries a day_zero stamp" in e for e in errors)


def test_cli_freeze_fetches_the_commit_and_refuses_a_second_write(
    registry_file, fake_mind, web, tmp_path, monkeypatch, capsys
):
    out = tmp_path / "out"
    out.mkdir()
    doc = fixture_doc("setup_summary_v3.json")
    web.publish(GH, SHA_A, "dashboard/summary.json", doc)
    monkeypatch.setattr(ingest, "unresolved_decisions", lambda doc, root=None: [])
    args = [
        "--registry",
        str(registry_file),
        "freeze",
        "--mind",
        str(fake_mind),
        "--out",
        str(out),
        "--instance",
        "lens",
        "--commit",
        SHA_A,
    ]
    assert cli.main(args) == 0
    assert "ok   freeze: snapshots/day_zero/lens.json" in capsys.readouterr().out
    snap = json.loads((out / "snapshots" / "day_zero" / "lens.json").read_text())
    assert snap["commit"] == SHA_A and snap["summary_path"] == "dashboard/summary.json"
    assert cli.main(args) == 1
    assert "never rewritten" in capsys.readouterr().out
