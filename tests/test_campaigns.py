"""Campaign state is distinct from timing evidence and survives board refreshes."""

import copy
import hashlib
from pathlib import Path

import pytest
import yaml

from pulse import ORGAN_ROOT, board, campaigns


def write_ledger(root, data):
    (root / "campaigns.yaml").write_text(yaml.safe_dump(data))
    for t in data["tasks"]:
        p = root / t["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("Task contract\n")


def test_migration_keeps_original_text_and_every_task():
    ledger = campaigns.load()
    migration = yaml.safe_load((ORGAN_ROOT / "migration.yaml").read_text())
    mapped = {t["destination"] for t in migration["tasks"]}
    assert mapped <= {t["path"] for t in ledger["tasks"]}
    assert len(mapped) == len(migration["tasks"])
    for row in migration["tasks"]:
        text = (ORGAN_ROOT / row["destination"]).read_text()
        original = text.split("\n---\n\n", 1)[1]
        assert hashlib.sha256(original.encode()).hexdigest() == row["sha256"]
        assert migration["source_commit"] in text
        assert row["source"] in text


@pytest.mark.parametrize(
    "mutation", ["duplicate", "campaign", "status", "missing", "escape", "url"]
)
def test_invalid_ledgers_fail_closed(tmp_path, mutation):
    data = copy.deepcopy(campaigns.load())
    write_ledger(tmp_path, data)
    task = data["tasks"][0]
    if mutation == "duplicate":
        data["tasks"].append(copy.deepcopy(task))
    elif mutation == "campaign":
        task["campaign"] = "unknown"
    elif mutation == "status":
        task["status"] = "maybe"
    elif mutation == "missing":
        task["path"] = "tasks/missing.md"
    elif mutation == "escape":
        task["path"] = "tasks/../campaigns.yaml"
    else:
        data["campaigns"][0]["evidence"] = "javascript:alert(1)"
    (tmp_path / "campaigns.yaml").write_text(yaml.safe_dump(data))
    with pytest.raises(campaigns.CampaignError):
        campaigns.load(tmp_path)


def test_control_room_precedes_measurements_and_escapes():
    data = copy.deepcopy(campaigns.load())
    data["campaigns"][0]["title"] = "<script>alert(1)</script>"
    for text in (
        board.render_html([], campaign_data=data),
        board.render_markdown([], campaign_data=data),
    ):
        # Check content order independently of the section navigation labels.
        if "<main>" in text:
            text = text.split("<main>", 1)[1]
        assert (
            text.index("Profiling Check In")
            < text.index("Active campaigns")
            < text.index("Active tasks")
            < text.index("Profiling evidence")
        )
    page = board.render_html([], campaign_data=data)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
    assert "field.value" in page  # copy the edited value, not a frozen default
    assert "Select and copy the prompt above." in page


def test_refresh_does_not_stamp_checkin_or_change_qualification(tmp_path):
    data = campaigns.load()
    original = (ORGAN_ROOT / "campaigns.yaml").read_bytes()
    before = board.render_state([], updated="2026-10-03T00:00:00Z")
    board.write([], tmp_path, updated="2026-10-03T00:00:00Z")
    assert (ORGAN_ROOT / "campaigns.yaml").read_bytes() == original
    assert campaigns.marker(data) in (tmp_path / "dashboard.html").read_text()
    import json

    assert json.loads((tmp_path / "state.json").read_text()) == before


def test_missing_ledger_is_not_an_empty_success(tmp_path):
    with pytest.raises(campaigns.CampaignError, match="missing campaign ledger"):
        campaigns.load(tmp_path)


def test_each_open_task_is_inside_its_campaign_and_links_are_separate():
    import html
    import re

    data = campaigns.load()
    page = campaigns.render_html(data)
    for campaign in data["campaigns"]:
        if campaign["status"] in campaigns.CLOSED:
            continue
        section = re.search(r'<details id="campaign-' + campaign["id"] + r'".*?</details>', page)[0]
        expected = [
            t
            for t in data["tasks"]
            if t["campaign"] == campaign["id"] and t["status"] not in campaigns.CLOSED
        ]
        assert section.count('<article class="campaign-task">') == len(expected)
        for task in expected:
            assert html.escape(task["title"]) in section
            assert campaigns.URL + task["path"] in section
        assert 'aria-label="Tasks for ' + html.escape(campaign["title"], quote=True) in page
        if campaign.get("evidence"):
            assert 'aria-label="Evidence for ' + html.escape(campaign["title"], quote=True) in page
