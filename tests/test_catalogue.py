"""Scientifically incompatible and malformed feeds cannot become references."""

import copy
import json

import pytest
import yaml
from conftest import SHA_A, SHA_B, fixture_doc

from pulse import board, ingest, registry, summary

V2 = ("profiling-summary", 2)


@pytest.fixture
def doc():
    return fixture_doc("setup_summary_v2.json")


def test_multi_axis_catalogue_and_v1_coexist(doc):
    assert summary.classify(doc, V2) == ("ok", [])
    assert summary.classify(fixture_doc("lens_summary_v1.json"))[0] == "ok"
    assert summary.classify(doc, ("profiling-summary", 1))[0] == "unsupported"
    assert summary.pair(doc) == []
    assert summary.qualified_records(doc) == 4


def test_empty_catalogue_is_valid_but_not_a_pass(doc):
    for key in ("setups", "records", "selections", "hazards", "recommendations"):
        doc[key] = []
    doc["coverage"] = {
        "expected": {"cells": 0},
        "observed": {"setups": 0, "records": 0, "selected": 0},
        "excluded": [],
    }
    assert summary.classify(doc) == ("ok", [])
    assert summary.qualified_records(doc) == 0


@pytest.mark.parametrize("field", ["setups", "records", "selections", "hazards", "recommendations"])
@pytest.mark.parametrize("bad", [None, {}, 7, "wrong", [None]])
def test_catalogue_collections_are_validated_without_crashing(doc, field, bad):
    doc[field] = bad
    assert summary.classify(doc)[0] == "invalid"


@pytest.mark.parametrize("field", ["setups", "records", "selections", "hazards", "recommendations"])
def test_duplicate_semantic_ids_are_rejected(doc, field):
    doc[field].append(copy.deepcopy(doc[field][0]))
    assert any("duplicate id" in e for e in summary.validate(doc))


@pytest.mark.parametrize(
    "path,value,needle",
    [
        (("records", 0, "setup_id"), "nonexistent", "unknown reference"),
        (("records", 0, "axis"), {}, "axis"),
        (("records", 0, "unit"), "MiB", "unit"),
        (("records", 0, "measurement", "single_call"), -1, "non-negative"),
        (("records", 0, "measurement", "single_call"), True, "non-negative"),
        (("records", 0, "measurement", "single_call"), None, "non-negative"),
        (("records", 0, "measurement", "single_call"), float("nan"), "non-finite"),
        (("records", 0, "measurement", "single_call"), float("inf"), "non-finite"),
        (("records", 0, "method", "repetitions"), 0, "repetitions"),
        (("records", 0, "method", "repetitions"), True, "repetitions"),
        (("records", 0, "method", "cache_state"), None, "unknowns reason"),
        (("records", 0, "provenance", "measured_at"), "2026-10-04", "measured_at"),
        (("records", 0, "provenance", "qualified"), False, "qualified"),
        (("records", 0, "provenance", "has_provenance"), False, "requires provenance"),
        (("records", 0, "identity", "software"), {}, "software"),
        (("records", 3, "metric"), "vram", "metric"),
        (("selections", 0, "record_id"), "nonexistent", "unknown reference"),
        (("selections", 0, "record_id"), None, "unknown reference"),
        (("selections", 0, "axis"), "compile", "axis mismatch"),
        (("selections", 0, "metric"), "batch_per_call", "metric mismatch"),
        (("selections", 0, "method_id"), "different-warmup", "method mismatch"),
        (("selections", 0, "host"), "other-host", "host mismatch"),
        (("selections", 0, "identity", "precision"), "mixed", "identity mismatch"),
        (("selections", 0, "identity", "library_version"), "2026.1.1", "identity mismatch"),
        (
            ("selections", 0, "identity", "software", "PyAutoArray"),
            "other-sha",
            "identity mismatch",
        ),
        (("selections", 4, "record_id"), "runtime-fixture", "cannot select"),
        (("selections", 4, "reason"), "", "reason"),
        (("coverage", "expected", "cells"), 6, "declared selection count"),
        (("coverage", "observed", "records"), 9, "catalogue contents"),
        (("setups", 0, "configuration", "psf_shape", "value"), [float("inf"), 21], "non-finite"),
        (("setups", 0, "configuration", "oversampling", "reason"), "", "reason"),
        (("hazards", 0, "applies_to", "setup_ids"), [], "must not be empty"),
        (("recommendations", 0, "record_ids"), ["missing"], "unknown reference"),
        (
            ("recommendations", 0, "applies_to", "library_versions"),
            ["2020.1.1"],
            "outside applicable",
        ),
    ],
)
def test_bad_evidence_cannot_be_selected(doc, path, value, needle):
    target = doc
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    outcome, errors = summary.classify(doc)
    assert outcome == "invalid"
    assert any(needle in e for e in errors), errors


@pytest.mark.parametrize("field", ["records", "hazards", "recommendations"])
@pytest.mark.parametrize(
    "path", ["/private/x", "../x", "results/../x", "https://example.invalid/x", "results\\x"]
)
def test_unsafe_evidence_links_are_rejected(doc, field, path):
    evidence = doc[field][0]["evidence"]
    (evidence if field == "records" else evidence[0])["path"] = path
    assert any("unsafe evidence" in e for e in summary.validate(doc))


def test_two_records_cannot_compete_for_one_selection_slot(doc):
    extra = copy.deepcopy(doc["selections"][0])
    extra["id"] = "different-label-same-slot"
    doc["selections"].append(extra)
    assert any("duplicate measurement slot" in e for e in summary.validate(doc))


def test_selected_setup_cannot_change_solver_or_regularization(doc):
    alternate = copy.deepcopy(doc["setups"][0])
    alternate.update(id="other-setup", configuration_id="other-configuration")
    alternate["configuration"]["solver"]["value"] = "different-solver"
    doc["setups"].append(alternate)
    doc["selections"][0]["setup_id"] = alternate["id"]
    assert any("setup_id mismatch" in e for e in summary.validate(doc))


def test_legacy_evidence_can_be_unreviewed_but_not_promoted(doc):
    r = doc["records"][0]
    r["validation"] = {"status": "unreviewed", "reason": "legacy evidence"}
    r["provenance"].update(
        qualified=False,
        has_provenance=False,
        measured_at=None,
        unknowns={"measured_at": "not recorded"},
    )
    doc["selections"][0]["status"] = "unreviewed"
    doc["recommendations"][0]["validation"]["status"] = "unreviewed"
    assert summary.validate(doc) == []
    doc["selections"][0]["status"] = "accepted"
    assert any("validation status mismatch" in e for e in summary.validate(doc))


def test_accepted_recommendation_cannot_rest_on_unreviewed_evidence(doc):
    doc["records"][0]["validation"]["status"] = "unreviewed"
    doc["selections"][0]["status"] = "unreviewed"
    assert any("accepted supporting records" in e for e in summary.validate(doc))


@pytest.mark.parametrize(
    "schema,version",
    [("profiling-summary", 3), ("profiling-summary", True), ([], 2), ("profiling-summary", {})],
)
def test_bad_versions_fail_closed_without_crashing(doc, schema, version):
    doc.update(schema=schema, version=version)
    assert summary.classify(doc)[0] == "unsupported"


def test_v2_receipts_render_and_preserve_last_good_snapshot(
    doc, registry_file, fake_mind, web, tmp_path
):
    config = yaml.safe_load(registry_file.read_text())
    config["instances"][0]["supported_schema"] = "profiling-summary@2"
    registry_file.write_text(yaml.safe_dump(config))
    instance = registry.load(registry_file, mind=fake_mind)[0]
    gh, path = "PyAutoLabs/autolens_profiling", "dashboard/summary.json"
    web.publish(gh, SHA_A, path, doc)
    good = ingest.ingest(instance, tmp_path, now="2026-10-05T12:00:00Z")
    assert good.outcome == "ok" and good.commit == SHA_A
    assert ingest.read_receipt(tmp_path, "lens")["version"] == 2
    assert board.render_html([good]) and board.render_markdown([good])
    before = json.dumps(good.doc, sort_keys=True)
    doc["selections"][0]["record_id"] = "missing"
    web.publish(gh, SHA_B, path, doc)
    failed = ingest.ingest(instance, tmp_path, now="2026-10-05T13:00:00Z")
    assert failed.outcome == "invalid" and failed.cached
    assert failed.commit == SHA_A and failed.attempt_commit == SHA_B
    assert json.dumps(failed.doc, sort_keys=True) == before
    assert board.render_html([failed])


@pytest.mark.parametrize("value", [None, [], {}, True, 0, "", float("nan")])
def test_malformed_nested_fields_return_errors_not_exceptions(doc, value):
    """A corrupt field must not crash ingestion and lose the last-good fallback."""
    paths = []

    def walk(obj, prefix=()):
        items = (
            obj.items()
            if isinstance(obj, dict)
            else enumerate(obj)
            if isinstance(obj, list)
            else []
        )
        for key, child in items:
            paths.append((*prefix, key))
            walk(child, (*prefix, key))

    walk(doc)
    for path in paths:
        changed = copy.deepcopy(doc)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        outcome, errors = summary.classify(changed)
        assert outcome in ("ok", "invalid", "unsupported"), (path, outcome, errors)


def test_method_ids_cannot_hide_different_measurement_procedures(doc):
    other = copy.deepcopy(doc["records"][0])
    other["id"] = "other-run"
    other["method"]["statistic"] = "minimum"
    doc["records"].append(other)
    assert any("conflicting definitions" in e for e in summary.validate(doc))
