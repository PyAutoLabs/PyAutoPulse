"""One-commit ingest, receipts, last-good snapshots and cached semantics."""

import json
import subprocess

import pytest
from conftest import SHA_A, SHA_B, fixture_doc

from pulse import ingest, registry

GH = "PyAutoLabs/autolens_profiling"
PATH = "dashboard/summary.json"


@pytest.fixture
def lens(registry_file, fake_mind):
    return registry.get(registry.load(registry_file, mind=fake_mind), "lens")


def test_ok_reads_the_file_at_the_resolved_commit(lens, web, tmp_path, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "t0k")
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    assert s.outcome == "ok" and not s.cached and s.commit == SHA_A
    api, raw = (r.full_url for r in web.requests)
    assert api == f"https://api.github.com/repos/{GH}/commits/main"
    assert raw == f"https://raw.githubusercontent.com/{GH}/{SHA_A}/{PATH}"
    assert web.requests[0].get_header("Authorization") == "Bearer t0k"
    assert web.requests[1].get_header("Authorization") is None  # the token never leaves the API
    assert web.requests[0].get_header("User-agent") == ingest.USER_AGENT
    receipt = ingest.read_receipt(tmp_path, "lens")
    assert receipt["resolved_commit"] == SHA_A and receipt["outcome"] == "ok"
    assert receipt["record_count"] == 11 and receipt["errors"] == []
    assert receipt["cached_from"] is None
    snap = ingest.read_snapshot(tmp_path, "lens")
    assert snap["commit"] == SHA_A and snap["fetched_at"] == "2026-10-02T00:00:00Z"


def test_unchanged_refresh_advances_observation_not_capture(lens, web, tmp_path):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    before = {p: p.read_bytes() for p in tmp_path.glob("*s/lens.json")}
    ingest.ingest(lens, tmp_path, now="2026-10-03T00:00:00Z")
    assert (
        ingest.snapshot_path(tmp_path, "lens").read_bytes()
        == before[ingest.snapshot_path(tmp_path, "lens")]
    )
    replay = ingest.ingest(lens, tmp_path, offline=True)
    assert replay.fetched_at == "2026-10-02T00:00:00Z"
    assert replay.refreshed_at == "2026-10-03T00:00:00Z"
    assert ingest.read_receipt(tmp_path, "lens")["fetched_at"] == "2026-10-02T00:00:00Z"
    web.publish(GH, SHA_B, PATH, fixture_doc("lens_summary_v1.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-04T00:00:00Z")
    assert s.commit == SHA_B and s.fetched_at == "2026-10-04T00:00:00Z"


def test_unavailable_keeps_the_cached_snapshot_with_its_original_times(lens, web, tmp_path):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    good = ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    web.down = True
    s = ingest.ingest(lens, tmp_path, now="2026-10-09T00:00:00Z")
    assert s.outcome == "unavailable" and s.cached
    assert s.refreshed_at is None
    assert s.commit == SHA_A and s.fetched_at == "2026-10-02T00:00:00Z"
    assert s.doc["evidence_updated_at"] == good.doc["evidence_updated_at"]
    assert "connection reset" in s.errors[0]
    receipt = ingest.read_receipt(tmp_path, "lens")
    assert receipt["outcome"] == "unavailable" and receipt["resolved_commit"] is None
    assert receipt["fetched_at"] == "2026-10-09T00:00:00Z"
    assert receipt["cached_from"] == "2026-10-02T00:00:00Z"


def test_unavailable_with_no_snapshot_has_nothing_to_show(lens, tmp_path):
    s = ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")  # no_network refuses
    assert s.outcome == "unavailable" and s.doc is None and not s.cached
    assert ingest.read_snapshot(tmp_path, "lens") is None


@pytest.mark.parametrize(
    "fixture, outcome",
    [("unsupported_schema.json", "unsupported"), ("duplicate_id.json", "invalid")],
)
def test_bad_feeds_fail_and_keep_the_last_good_snapshot(lens, web, tmp_path, fixture, outcome):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    web.publish(GH, SHA_B, PATH, fixture_doc(fixture))
    s = ingest.ingest(lens, tmp_path, now="2026-10-03T00:00:00Z")
    assert s.outcome == outcome and s.cached
    assert s.commit == SHA_A and s.attempt_commit == SHA_B
    assert ingest.read_snapshot(tmp_path, "lens")["commit"] == SHA_A


def test_not_json_is_invalid(lens, web, tmp_path):
    web.publish(GH, SHA_A, PATH, b"<html>404</html>")
    s = ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    assert s.outcome == "invalid" and "not JSON" in s.errors[0]


def test_offline_reads_committed_files_and_writes_nothing(lens, web, tmp_path):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    ingest.ingest(lens, tmp_path, now="2026-10-02T00:00:00Z")
    web.requests.clear()
    s = ingest.ingest(lens, tmp_path, offline=True)
    assert s.outcome == "ok" and s.commit == SHA_A and web.requests == []


def test_a_local_read_reports_revision_and_dirty_state_and_writes_nothing(lens, tmp_path):
    checkout = tmp_path / "autolens_profiling"
    (checkout / "dashboard").mkdir(parents=True)
    (checkout / PATH).write_text(json.dumps(fixture_doc("valid_empty.json")))
    git = ["git", "-C", str(checkout), "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-qm", "x"], check=True)
    out = tmp_path / "organ"
    s = ingest.ingest(lens, out, local_path=checkout)
    assert s.source == "local" and s.dirty is False and len(s.commit) == 40
    (checkout / "scratch.txt").write_text("edit")
    assert ingest.ingest(lens, out, local_path=checkout).dirty is True
    assert not (out / "receipts").exists() and not (out / "snapshots").exists()


# ------------------------------------------- v3 decision resolution, counts ---


def _v3_lens(registry_file, fake_mind, schema="profiling-summary@3"):
    import yaml

    config = yaml.safe_load(registry_file.read_text())
    config["instances"][0]["supported_schema"] = schema
    registry_file.write_text(yaml.safe_dump(config))
    return registry.get(registry.load(registry_file, mind=fake_mind), "lens")


def _decisions(root, ids):
    import yaml

    rows = [
        {
            "id": key,
            "title": f"Designate {key}",
            "date": "2026-10-21",
            "url": f"https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/{key}.md",
        }
        for key in ids
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "decisions.yaml").write_text(yaml.safe_dump({"decisions": rows}))
    (root / "decisions").mkdir(exist_ok=True)
    for row in rows:
        (root / "decisions" / f"{row['id']}.md").write_text(
            f"# {row['title']}\n\nDate: {row['date']}\n"
        )


def test_v3_decision_ids_resolve_and_the_receipt_counts_lifecycle(
    registry_file, fake_mind, web, tmp_path
):
    lens = _v3_lens(registry_file, fake_mind)
    _decisions(tmp_path, ["fixture-designation"])
    web.publish(GH, SHA_A, PATH, fixture_doc("setup_summary_v3.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-21T00:00:00Z")
    assert s.outcome == "ok", s.errors
    receipt = ingest.read_receipt(tmp_path, "lens")
    assert (receipt["schema"], receipt["version"]) == ("profiling-summary", 3)
    assert receipt["lifecycle"] == {"current": 5, "superseded": 1, "archived": 3}


def test_v3_unresolved_decision_is_invalid_and_keeps_the_last_good(
    registry_file, fake_mind, web, tmp_path
):
    lens = _v3_lens(registry_file, fake_mind)
    _decisions(tmp_path, ["fixture-designation"])
    web.publish(GH, SHA_A, PATH, fixture_doc("setup_summary_v3.json"))
    ingest.ingest(lens, tmp_path, now="2026-10-21T00:00:00Z")
    _decisions(tmp_path, ["some-other-decision"])
    (tmp_path / "decisions/fixture-designation.md").unlink()
    web.publish(GH, SHA_B, PATH, fixture_doc("setup_summary_v3.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-22T00:00:00Z")
    assert s.outcome == "invalid" and s.cached and s.commit == SHA_A
    assert any("'fixture-designation' does not resolve" in e for e in s.errors)


def test_v3_without_a_decision_index_cannot_resolve(registry_file, fake_mind, web, tmp_path):
    lens = _v3_lens(registry_file, fake_mind)
    web.publish(GH, SHA_A, PATH, fixture_doc("setup_summary_v3.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-21T00:00:00Z")
    assert s.outcome == "invalid"
    assert "decision index unreadable" in s.errors[0]


def test_v2_and_walltime_receipts_keep_their_shape(registry_file, fake_mind, web, tmp_path):
    lens = _v3_lens(registry_file, fake_mind, "walltime-validation@1")
    web.publish(GH, SHA_A, PATH, fixture_doc("walltime_validation_v1.json"))
    s = ingest.ingest(lens, tmp_path, now="2026-10-21T00:00:00Z")
    assert s.outcome == "ok", s.errors
    receipt = ingest.read_receipt(tmp_path, "lens")
    assert receipt["schema"] == "walltime-validation" and "lifecycle" not in receipt
    assert receipt["record_count"] == 2
