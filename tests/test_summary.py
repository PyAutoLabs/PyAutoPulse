"""The profiling-summary v1 exchange contract and the comparison pairing."""

import copy
import math

import pytest
from conftest import FIXTURES, fixture_doc

from pulse import summary

V1 = ("profiling-summary", 1)


def test_the_reader_imports_no_scientific_library():
    import subprocess
    import sys

    code = (
        "import sys, json, pathlib; sys.path.insert(0, sys.argv[1]);"
        "from pulse import cli, summary;"
        "[summary.classify(json.loads(p.read_text())) for p in pathlib.Path(sys.argv[2]).glob('*.json')];"
        "bad = [m for m in ('numpy', 'autolens', 'autoarray', 'autofit', 'autogalaxy', 'jax')"
        " if m in sys.modules]; print(bad); sys.exit(1 if bad else 0)"
    )
    root = str(FIXTURES.parents[1])
    proc = subprocess.run(
        [sys.executable, "-c", code, root, str(FIXTURES)], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_trimmed_live_feed_validates_clean():
    doc = fixture_doc("lens_summary_v1.json")
    assert summary.classify(doc, V1) == ("ok", [])
    assert len(doc["records"]) <= 20 and len(doc["comparisons"]) == 5
    assert all(not p.refused for p in summary.pair(doc))


def test_valid_empty_feed_is_ok():
    assert summary.classify(fixture_doc("valid_empty.json"), V1) == ("ok", [])


def test_unsupported_version_is_refused_not_validated():
    outcome, errors = summary.classify(fixture_doc("unsupported_schema.json"), V1)
    assert outcome == "unsupported"
    assert "version 2" in errors[0]


def test_registered_schema_must_match():
    outcome, errors = summary.classify(fixture_doc("valid_empty.json"), ("inference-summary", 1))
    assert outcome == "unsupported"


def test_duplicate_record_id_is_invalid():
    outcome, errors = summary.classify(fixture_doc("duplicate_id.json"), V1)
    assert outcome == "invalid"
    assert any("duplicate record id" in e for e in errors)


def _mutate(fn):
    doc = copy.deepcopy(fixture_doc("unknown_provenance.json"))
    fn(doc)
    return summary.validate(doc)


@pytest.mark.parametrize(
    "mutation, needle",
    [
        (lambda d: d.pop("records"), "missing required field 'records'"),
        (lambda d: d.update(generated_at="2026-09-30 12:00"), "generated_at"),
        (lambda d: d.update(evidence_updated_at=None), "without evidence_updated_at_reason"),
        (lambda d: d.update(valid_until="2026-08-01T00:00:00Z"), "valid_until precedes"),
        (lambda d: d.update(producer_revision="HEAD"), "producer_revision"),
        (lambda d: d["records"][0]["measurement"].update(single_jit_s=math.nan), "non-finite"),
        (lambda d: d["records"][0]["measurement"].update(single_jit_s=math.inf), "non-finite"),
        (lambda d: d["records"][0].update(unit="MB"), "is not a runtime unit"),
        (lambda d: d["records"][0].update(axis="speed"), "axis 'speed'"),
        (lambda d: d["records"][0]["evidence"].update(path="../secret.json"), "evidence path"),
        (lambda d: d["records"][0]["evidence"].update(path="/home/x/r.json"), "evidence path"),
        (lambda d: d["records"][0]["evidence"].update(path="https://x/r.json"), "evidence path"),
        (lambda d: d["records"][0]["provenance"].pop("qualified"), "provenance.qualified"),
        (lambda d: d["comparisons"][0].update(status="regressed"), "status 'regressed'"),
        (lambda d: d["comparisons"][0].update(policy="other"), "is not comparison_policy.id"),
        (lambda d: d["coverage"]["observed"].update(points=-1), "non-negative"),
        (lambda d: d.update(limitations=[""]), "limitations"),
    ],
)
def test_contract_breaks_are_named(mutation, needle):
    errors = _mutate(mutation)
    assert any(needle in e for e in errors), errors


def test_a_memory_value_cannot_enter_a_seconds_series():
    errors = _mutate(lambda d: d["records"][0].update(unit="GiB"))
    assert any("cannot enter a series of another unit" in e for e in errors)


def test_unknown_provenance_is_kept_and_counted_unqualified():
    doc = fixture_doc("unknown_provenance.json")
    assert summary.classify(doc, V1)[0] == "ok"
    assert len(doc["records"]) == 2
    assert summary.qualified_records(doc) == 1


def test_compile_runtime_pair_is_refused_never_merged():
    (p,) = summary.pair(fixture_doc("axis_mismatch.json"))
    assert p.group == "refused"
    assert any("axis mismatch" in r for r in p.refused)


def test_changed_hardware_is_a_separate_group_and_a_mixed_pair_is_refused():
    pairs = summary.pair(fixture_doc("changed_hardware.json"))
    groups = [p.group for p in pairs]
    assert groups[0] == "cpu · cpu · float64"
    assert groups[1] == "a100 · gpu · float32"
    assert groups[2] == "refused"
    assert "hardware identity changed" in pairs[2].refused[0]


def test_an_unrecorded_host_is_unknown_not_different():
    doc = copy.deepcopy(fixture_doc("changed_hardware.json"))
    doc["records"][0]["provenance"]["host"] = None
    assert not summary.pair(doc)[0].refused


def test_a_missing_endpoint_is_refused():
    doc = copy.deepcopy(fixture_doc("unknown_provenance.json"))
    doc["comparisons"][0]["candidate"] = "9.9.9"
    (p,) = summary.pair(doc)
    assert p.group == "refused" and "not in records" in p.refused[0]


def test_second_producer_takes_the_same_code_path():
    doc = fixture_doc("second_producer.json")
    assert doc["project"] != "autolens_profiling"
    assert summary.classify(doc, V1) == ("ok", [])
    (p,) = summary.pair(doc)
    assert p.group == "a100 · gpu · mixed" and not p.refused
