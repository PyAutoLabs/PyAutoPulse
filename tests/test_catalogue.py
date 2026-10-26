"""Scientifically incompatible and malformed feeds cannot become references."""

import copy
import json

import pytest
import yaml
from conftest import SHA_A, SHA_B, fixture_doc

from pulse import board, catalogue, ingest, registry, summary

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
    [
        ("profiling-summary", 4),
        ("walltime-validation", 2),
        ("profiling-summary", True),
        ([], 2),
        ("profiling-summary", {}),
    ],
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


def test_the_autofit_profiling_producer_feed_validates_through_the_shared_reader():
    """Instance ``fit``: autofit_profiling's catalogue at its B4b branch (issue autofit_profiling#4:
    the B4a breakdown plus the EP / graphical baselines and the analytic parity cell), copied
    verbatim; read through the same code path as every producer."""
    doc = fixture_doc("autofit_profiling_v2.json")
    assert doc["project"] == "autofit_profiling"
    assert summary.classify(doc, ("profiling-summary", 2)) == ("ok", [])
    axes = {r["axis"] for r in doc["records"]}
    assert axes == {"runtime", "breakdown", "memory"}
    memory = [r for r in doc["records"] if r["axis"] == "memory"]
    assert memory and {(r["metric"], r["unit"]) for r in memory} == {("host_peak_rss", "KiB")}
    slots = [s for s in doc["selections"] if s["status"] == "inapplicable"]
    assert slots and all(s["record_id"] is None for s in slots)


# ---------------------------------------------------- profiling-summary@3 ---

V3 = ("profiling-summary", 3)


@pytest.fixture
def v3():
    return fixture_doc("setup_summary_v3.json")


def test_lifecycle_catalogue_validates_and_v2_is_unchanged(v3):
    assert summary.classify(v3, V3) == ("ok", [])
    assert summary.classify(v3, V2)[0] == "unsupported"
    assert summary.classify(fixture_doc("setup_summary_v2.json"), V2) == ("ok", [])
    assert summary.classify(fixture_doc("autofit_profiling_v2.json"), V2) == ("ok", [])
    assert catalogue.lifecycle_counts(v3) == {"current": 5, "superseded": 1, "archived": 3}
    assert catalogue.decision_ids(v3) == ["fixture-designation"]
    assert summary.pair(v3) == []


@pytest.mark.parametrize(
    "fixture,needle",
    [
        ("v3_duplicate_current.json", "second current record"),
        ("v3_optimal_without_decision.json", "class optimal requires a decision_id"),
        ("v3_laptop_current.json", "is never current"),
        ("v3_archived_in_records.json", "archive_record_count"),
    ],
)
def test_lifecycle_refusal_fixtures(fixture, needle):
    outcome, errors = summary.classify(fixture_doc(fixture), V3)
    assert outcome == "invalid"
    assert any(needle in e for e in errors), errors


@pytest.mark.parametrize(
    "path,value,needle",
    [
        (("records", 0, "setup_id"), "jax_gpu_dense", "must be 'jax_gpu_dense_fp64'"),
        (("records", 5, "setup_id"), "jax_cpu_dense_fp64", "jax_cpu_dense_fp64_nufft"),
        (("records", 0, "setup", "backend"), "torch", "setup.backend"),
        (("records", 0, "setup", "precision"), "fp32", "setup.precision"),
        (("records", 0, "setup", "threads"), 0, "threads"),
        (("records", 0, "likelihood", "dataset_type"), "pixelized", "dataset_type"),
        (("records", 0, "host_class"), "cloud", "host_class"),
        (("records", 0, "measurement"), "memory", "measurement"),
        (("records", 0, "unit"), "MiB", "unit"),
        (("records", 0, "class"), "fastest", "class"),
        (("records", 0, "status"), "latest", "status"),
        (("records", 0, "values"), {"other": 1.0}, "headline metric"),
        (("records", 0, "values", "single_call"), -1, "non-negative"),
        (("records", 0, "measured_at"), "2026-10-18", "measured_at"),
        (("records", 0, "figures", 0, "sha256"), "abc", "sha256"),
        (("records", 0, "figures", 0, "path"), "/abs.png", "unsafe figure path"),
        (
            ("records", 0, "superseded_by"),
            "imaging-delaunay-hst-a100-runtime-old",
            "only superseded",
        ),
        (("records", 1, "superseded_by"), "missing", "must name another record"),
        (("records", 1, "superseded_by"), None, "must name another record"),
        (("records", 3, "decision_id"), "", "string or null"),
        (("planned_cells", 0, "class"), None, "class"),
        (("planned_cells", 1), "cell", "must be an object"),
        (("archive_record_count",), -1, "archive_record_count"),
        (("archive_record_count",), True, "archive_record_count"),
        (("coverage", "expected", "cells"), 4, "planned_cells count"),
        (("coverage", "observed", "current"), 9, "observed.current"),
    ],
)
def test_lifecycle_contract_breaks_are_named(v3, path, value, needle):
    target = v3
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    outcome, errors = summary.classify(v3, V3)
    assert outcome == "invalid"
    assert any(needle in e for e in errors), errors


def test_planned_cells_carry_class_and_are_unique(v3):
    v3["planned_cells"][0].pop("class")
    assert any("planned_cells[0].class" in e for e in summary.validate(v3))
    v3 = fixture_doc("setup_summary_v3.json")
    v3["planned_cells"].append(copy.deepcopy(v3["planned_cells"][0]))
    v3["coverage"]["expected"]["cells"] += 1
    assert any("duplicate planned cell" in e for e in summary.validate(v3))


def test_one_current_per_key_counts_host_class_and_variant_as_identity(v3):
    other = copy.deepcopy(v3["records"][3])
    other.update(id="light-fixed", model_variant="light_fixed")
    v3["records"].append(other)
    v3["coverage"]["observed"].update(records=7, current=6)
    assert summary.classify(v3, V3) == ("ok", [])
    clash = copy.deepcopy(v3["records"][3])
    clash["id"] = "clash"
    v3["records"].append(clash)
    v3["coverage"]["observed"].update(records=8, current=7)
    assert any("second current record 'clash'" in e for e in summary.validate(v3))


def test_a_size_variant_is_current_beside_its_standard_row(v3):
    # The regime (source-size bin) is part of the one-current key: a current
    # source_pixels_784 row validates beside the current standard row.
    size = copy.deepcopy(v3["records"][0])
    size.update(id="size-784", regime="source_pixels_784")
    v3["records"].append(size)
    v3["coverage"]["observed"].update(records=7, current=6)
    assert summary.classify(v3, V3) == ("ok", [])
    clash = copy.deepcopy(size)
    clash["id"] = "clash-784"
    v3["records"].append(clash)
    v3["coverage"]["observed"].update(records=8, current=7)
    errors = summary.validate(v3)
    assert any("second current record 'clash-784'" in e for e in errors)
    assert any(
        "(likelihood, instrument, setup_id, host_class, model_variant, measurement, regime)" in e
        for e in errors
    )


def test_a_planned_cell_without_a_regime_is_covered_by_any_regime():
    cell = {"instrument": "hst", "setup_id": "s", "host_class": "hpc_a100"}
    cell.update(likelihood={"dataset_type": "imaging", "variant": "x"})
    cell.update(model_variant="default", measurement="runtime")
    record = dict(cell, regime="n_vis_lt_1e5")
    assert catalogue.covers(record, cell)
    assert catalogue.covers(record, dict(cell, regime="n_vis_lt_1e5"))
    assert not catalogue.covers(record, dict(cell, regime="standard"))
    assert catalogue.lifecycle_key(record) != catalogue.lifecycle_key(cell)


def test_local_gpu_rows_may_be_kept_but_never_current(v3):
    row = copy.deepcopy(v3["records"][4])
    row.update(id="laptop-gpu", host_class="local_gpu", status="superseded")
    row["superseded_by"] = v3["records"][4]["id"]
    v3["records"].append(row)
    v3["coverage"]["observed"].update(records=7, superseded=2)
    assert summary.classify(v3, V3) == ("ok", [])
    row["status"], row["superseded_by"] = "current", None
    row["model_variant"] = "laptop"
    v3["coverage"]["observed"].update(current=6, superseded=1)
    assert any("'local_gpu' is never current" in e for e in summary.validate(v3))


@pytest.mark.parametrize("value", [None, [], {}, True, 0, "", float("nan")])
def test_malformed_v3_fields_return_errors_not_exceptions(v3, value):
    def paths(obj, prefix=()):
        items = (
            obj.items()
            if isinstance(obj, dict)
            else enumerate(obj)
            if isinstance(obj, list)
            else []
        )
        for key, child in items:
            yield (*prefix, key)
            yield from paths(child, (*prefix, key))

    for path in list(paths(v3))[::3]:
        changed = copy.deepcopy(v3)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        outcome, errors = summary.classify(changed)
        assert outcome in ("ok", "invalid", "unsupported"), (path, outcome, errors)


# ------------------- v3 resources and projected node throughput (phase 2x) ---

PNT = "projected_node_throughput"


def test_resources_and_node_throughput_are_optional_and_additive(v3):
    assert summary.classify(v3, V3) == ("ok", [])
    for record in v3["records"]:
        record.pop("resources", None)
        record.pop(PNT, None)
    assert summary.classify(v3, V3) == ("ok", [])


@pytest.mark.parametrize(
    "path,value,needle",
    [
        ((0, "resources"), [], "resources: must be an object"),
        ((0, "resources", "cpus_per_eval"), 0, "cpus_per_eval"),
        ((0, "resources", "cpus_per_eval"), 1.5, "cpus_per_eval"),
        ((0, "resources", "cpus_per_eval"), None, "cpus_per_eval is null without a reason"),
        ((0, "resources", "devices_per_eval"), -1, "devices_per_eval"),
        ((0, "resources", "peak_rss_gb"), -2.0, "peak_rss_gb"),
        ((0, "resources", "peak_rss_gb"), float("nan"), "peak_rss_gb"),
        ((0, "resources", "peak_rss_gb"), None, "peak_rss_gb is null without a reason"),
        ((0, "resources", "source"), "", "resources.source"),
        ((5, "resources", "peak_rss_reason"), "", "peak_rss_reason"),
        ((0, PNT), "248 calls/s", "projected_node_throughput: must be an object"),
        ((0, PNT, "basis"), "measured", "must be 'projected'"),
        ((0, PNT, "status"), "estimated", "status"),
        ((0, PNT, "per_call_s"), 0, "per_call_s"),
        ((0, PNT, "per_call_s"), None, "a projected record needs per_call_s"),
        ((0, PNT, "per_call_source"), None, "per_call_source"),
        ((0, PNT, "parallel_efficiency"), 1.0, "parallel_efficiency: must be an object"),
        ((0, PNT, "parallel_efficiency", "value"), 1.2, "in (0, 1]"),
        ((0, PNT, "parallel_efficiency", "value"), 0, "in (0, 1]"),
        ((0, PNT, "parallel_efficiency", "source"), "", "parallel_efficiency.source"),
        ((0, PNT, "not_modelled"), [], "not_modelled"),
        ((0, PNT, "not_modelled"), None, "not_modelled"),
        ((0, PNT, "hosts"), [], "exactly one host"),
        ((0, PNT, "hosts", 0, "host_class"), "hpc_ral_cpu", "never projected onto another"),
        ((0, PNT, "hosts", 0, "workers"), 0, "workers"),
        ((0, PNT, "hosts", 0, "workers"), 82, "must name the smallest limit"),
        ((0, PNT, "hosts", 0, "bound_by"), "memory", "must name the smallest limit"),
        ((0, PNT, "hosts", 0, "bound_by"), "bandwidth", "bound_by"),
        ((0, PNT, "hosts", 0, "limits"), {}, "limits"),
        ((0, PNT, "hosts", 0, "limits", "disk"), 9, "limits key"),
        ((0, PNT, "hosts", 0, "limits", "cores"), 0, "limits.cores"),
        ((3, PNT, "hosts", 0, "limits", "gpus"), 4, "a gpus limit belongs to a gpu setup"),
        ((0, PNT, "hosts", 0, "calls_per_s"), float("inf"), "calls_per_s"),
        ((0, PNT, "hosts", 0, "calls_per_s"), None, "calls_per_s"),
        ((5, PNT, "reason"), None, "projected_node_throughput.reason"),
        ((5, PNT, "hosts"), [{"host": "x"}], "a not_projected record names no host"),
    ],
)
def test_malformed_node_throughput_blocks_are_refused(v3, path, value, needle):
    target = v3["records"]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    outcome, errors = summary.classify(v3, V3)
    assert outcome == "invalid"
    assert any(needle in e for e in errors), errors


def test_node_throughput_only_on_runtime_records(v3):
    v3["records"][2][PNT] = copy.deepcopy(v3["records"][0][PNT])
    errors = summary.validate(v3)
    assert any("only runtime records carry" in e for e in errors), errors


def test_gpu_projection_must_declare_its_gpu_limit(v3):
    v3["records"][0][PNT]["hosts"][0]["limits"].pop("gpus")
    v3["records"][0][PNT]["hosts"][0].update(bound_by="memory", workers=82)
    errors = summary.validate(v3)
    assert any("a gpus limit belongs to a gpu setup" in e for e in errors), errors


def test_unknown_resources_carry_a_reason(v3):
    resources = v3["records"][0]["resources"]
    resources.update(cpus_per_eval=None, peak_rss_gb=None, source=None)
    resources["reason"] = "The row predates the resources block and has no backfill entry."
    assert summary.classify(v3, V3) == ("ok", [])
