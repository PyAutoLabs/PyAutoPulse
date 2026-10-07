"""Browser transport uses the captured commit, not the producer's build revision."""

import json
import re
from dataclasses import replace

from conftest import SHA_A, fixture_doc

from pulse import board, setup_browser
from pulse.ingest import Snapshot
from pulse.registry import Instance


def capture():
    instance = Instance(
        "lens",
        "autolens_profiling",
        "dashboard/catalogue.json",
        "profiling-summary@2",
        "https://example.invalid",
        github="PyAutoLabs/autolens_profiling",
    )
    return Snapshot(
        instance,
        "ok",
        "remote",
        fixture_doc("setup_summary_v2.json"),
        SHA_A,
        "2026-10-05T00:00:00Z",
    )


def payload(page):
    return json.loads(re.search(r'class="setup-payload">(.*?)</script>', page, re.S)[1])


def test_transport_is_pinned_to_capture_not_producer():
    snapshot = capture()
    data = payload(setup_browser.render(snapshot))
    assert data["commit"] != data["catalogue"]["producer_revision"]
    assert (
        data["shard_base"]
        == f"https://raw.githubusercontent.com/PyAutoLabs/autolens_profiling/{SHA_A}/dashboard/"
    )
    assert data["remote_shards"] is True
    assert (
        payload(setup_browser.render(replace(snapshot, source="local", dirty=True)))[
            "remote_shards"
        ]
        is False
    )


def test_embedded_catalogue_cannot_end_script_element():
    snapshot = capture()
    snapshot.doc["setups"][0]["model"] = '</script><script>alert("unsafe")</script>'
    page = setup_browser.render(snapshot)
    assert "</script><script>alert" not in page
    assert payload(page)["catalogue"] == snapshot.doc


def test_legacy_and_failed_capture_remain_accessible():
    snapshot = capture()
    assert setup_browser.render(replace(snapshot, doc=fixture_doc("lens_summary_v1.json"))) == ""
    page = board.render_html(
        [replace(snapshot, outcome="unavailable", cached=True, errors=["offline"])]
    )
    assert "capture, qualification and legacy diagnostics" not in page
    assert "cached" in page.lower()
    assert 'data-setup-browser="lens"' in page
    assert "Original setup evidence (JavaScript disabled)" in page


def test_markdown_keeps_diagnostics_collapsed():
    page = board.render_markdown([capture()])
    assert "<details><summary>Capture, qualification and legacy diagnostics" in page
    assert "| Where | Count |" not in page


def test_real_browser_fixture_preserves_capture_hashes_and_setup_identity():
    import hashlib
    from pathlib import Path

    from pulse import catalogue

    fixture = json.loads((Path(__file__).parent / "fixtures/browser_measurements.json").read_text())
    assert len(fixture["capture_commit"]) == 40
    assert catalogue.validate(fixture["catalogue"]) == []
    for manifest in fixture["catalogue"]["evidence_shards"]:
        raw = fixture["shards"][manifest["path"]]
        assert hashlib.sha256(raw.encode()).hexdigest() == manifest["sha256"]
        shard = json.loads(raw)
        assert catalogue.validate(shard) == []
        assert len(shard["records"]) == manifest["records"]
        assert shard["setups"] == [
            setup for setup in fixture["catalogue"]["setups"] if setup["id"] == manifest["setup_id"]
        ]
