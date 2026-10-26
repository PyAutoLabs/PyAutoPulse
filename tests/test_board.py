"""The board: three notions, producer comparisons verbatim, cached semantics, state.json."""

import json
import re

import pytest
from conftest import SHA_A, SHA_G, fixture_doc

from pulse import board, cli, ingest, registry

GH = "PyAutoLabs/autolens_profiling"
PATH = "dashboard/summary.json"
NOW = "2026-10-02T00:00:00Z"


@pytest.fixture
def lens(registry_file, fake_mind):
    return registry.get(registry.load(registry_file, mind=fake_mind), "lens")


def _view(lens, web, tmp_path, fixture, now=NOW):
    web.publish(GH, SHA_A, PATH, fixture_doc(fixture))
    return ingest.ingest(lens, tmp_path, now=now)


def _validator():
    mod = cli._state_validator()
    if mod is None:
        pytest.skip("no PyAutoBrain checkout here to validate state.json")
    return mod


def test_the_three_notions_are_separate_columns(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "lens_summary_v1.json")
    md = board.render_markdown([s], NOW)
    assert "| Integrity | Freshness | Qualification |" in md
    assert board.integrity(s) == "ok"
    assert board.freshness(s, NOW) == "freshness policy unspecified · age 46 d at fetch 2026-10-02"
    assert board.qualification(s).endswith("comparisons qualified")


def test_valid_empty_feed_says_no_measurements(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "valid_empty.json")
    md = board.render_markdown([s], NOW)
    assert "**No measurements.**" in md and "no measurements" in board.coverage(s)
    assert "all measurements passed" not in md.replace('"all measurements passed"', "")
    state = board.render_state([s], NOW, NOW)
    assert state["status"] == "yellow"
    assert any(i["text"].endswith("no measurements (a valid, empty feed)") for i in state["items"])


def test_cached_snapshot_is_labelled_and_never_re_aged(lens, web, tmp_path):
    _view(lens, web, tmp_path, "lens_summary_v1.json")
    web.down = True
    first = ingest.ingest(lens, tmp_path, now="2026-10-05T00:00:00Z")
    board.write([first], tmp_path, now="2026-10-05T00:00:00Z")
    md1 = (tmp_path / "dashboard.md").read_text()
    state1 = json.loads((tmp_path / "state.json").read_text())
    second = ingest.ingest(lens, tmp_path, now="2026-10-06T00:00:00Z")
    board.write([second], tmp_path, now="2026-10-06T00:00:00Z")
    md2 = (tmp_path / "dashboard.md").read_text()
    assert "**Cached:**" in md2 and "fetched 2026-10-02T00:00:00Z" in md2
    assert "evidence 2026-08-17" in md2 and "connection reset" in md2
    assert md1 == md2  # the second render re-aged nothing
    assert json.loads((tmp_path / "state.json").read_text())["updated"] == state1["updated"]
    assert board.integrity(second) == "cached · latest fetch unavailable"
    (cached,) = [i for i in state1["items"] if i["id"] == "pulse:lens:cached"]
    assert cached["severity"] == "yellow"


def test_failed_without_a_snapshot_is_red(lens, tmp_path):
    s = ingest.ingest(lens, tmp_path, now=NOW)
    state = board.render_state([s], NOW, NOW)
    assert state["status"] == "red"
    assert state["items"][0]["text"] == "lens: summary unavailable"
    assert "Unavailable:" in board.render_markdown([s], NOW)


def test_unsupported_is_red_even_with_a_cache(lens, web, tmp_path):
    _view(lens, web, tmp_path, "lens_summary_v1.json")
    s = _view(lens, web, tmp_path, "unsupported_schema.json")
    state = board.render_state([s], NOW, NOW)
    assert state["status"] == "red" and "unsupported" in state["items"][0]["text"]


def test_unknown_provenance_shows_unqualified_and_counts(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "unknown_provenance.json")
    assert board.qualification(s) == "1/2 records · 0/1 comparisons qualified"
    state = board.render_state([s], NOW, NOW)
    assert any(i["id"] == "pulse:lens:unqualified" for i in state["items"])


def test_refused_pairs_show_the_reason_and_no_ratio(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "axis_mismatch.json")
    md = board.render_markdown([s], NOW)
    assert "lens / refused by the reader (never combined)" in md
    assert "not shown (refused)" in md and "0.033" not in md
    assert "axis mismatch" in md


def test_changed_hardware_renders_separate_groups(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "changed_hardware.json")
    md = board.render_markdown([s], NOW)
    assert "### lens / comparisons on cpu · cpu · float64" in md
    assert "### lens / comparisons on a100 · gpu · float32" in md
    assert "hardware identity changed" in md


def test_ratios_are_the_producers_never_recomputed(lens, web, tmp_path):
    doc = fixture_doc("second_producer.json")
    doc["comparisons"][0]["ratio"] = 7.25  # deliberately not candidate/baseline
    web.publish(GH, SHA_A, PATH, doc)
    s = ingest.ingest(lens, tmp_path, now=NOW)
    md = board.render_markdown([s], NOW)
    assert "| 7.25 |" in md and "2.55" not in md


def test_drift_item_hands_off_to_profiling_triage(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "second_producer.json")
    state = board.render_state([s], NOW, NOW)
    key = "ellipse:hst/ellipse_fit/x7:gpu_mp"
    (item,) = [i for i in state["items"] if i["id"] == f"pulse:lens:drift:{key}"]
    assert item["severity"] == "yellow" and item["prompt"] == f"/profiling triage {key}"
    triage = item["actions"][0]
    assert triage == {
        "id": "triage",
        "label": "Hand off to profiling triage",
        "kind": "prompt",
        "target": f"/profiling triage {key}",
        "safety": "scientific_judgement",
    }
    assert item["actions"][1]["target"].startswith(f"https://github.com/{GH}/blob/{SHA_A}/")
    assert _validator().validate_state(state) == []


def test_unqualified_drift_is_a_contextual_info_flag(lens, web, tmp_path):
    doc = fixture_doc("second_producer.json")
    doc["comparisons"][0]["qualified"] = False
    web.publish(GH, SHA_A, PATH, doc)
    state = board.render_state([ingest.ingest(lens, tmp_path, now=NOW)], NOW, NOW)
    (item,) = [i for i in state["items"] if ":drift:" in i["id"]]
    assert item["severity"] == "info" and "contextual flag" in item["text"]


def test_no_freshness_policy_past_the_presentation_window_is_called_out(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "lens_summary_v1.json")
    state = board.render_state([s], NOW, "2027-01-01T00:00:00Z")
    assert any(i["id"] == "pulse:lens:aged" for i in state["items"])
    assert not any(i["id"] == "pulse:lens:aged" for i in board.render_state([s], NOW, NOW)["items"])


def test_an_expired_valid_until_is_stale(lens, web, tmp_path):
    doc = fixture_doc("unknown_provenance.json")
    doc["valid_until"] = "2026-09-15T00:00:00Z"
    web.publish(GH, SHA_A, PATH, doc)
    s = ingest.ingest(lens, tmp_path, now=NOW)
    assert board.freshness(s, NOW).startswith("stale")
    assert any(i["id"] == "pulse:lens:stale" for i in board.render_state([s], NOW, NOW)["items"])


def test_second_producer_renders_as_a_second_row_with_no_branching(
    two_registry_file, fake_mind, web, tmp_path
):
    instances = registry.load(two_registry_file, mind=fake_mind)
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    web.publish(
        "PyAutoLabs/autogalaxy_profiling",
        SHA_G,
        "out/profiling_summary.json",
        fixture_doc("second_producer.json"),
    )
    views = [ingest.ingest(i, tmp_path, now=NOW) for i in instances]
    md = board.render_markdown(views, NOW)
    assert "| [lens](#lens) (autolens_profiling) |" in md
    assert "| [galaxy](#galaxy) (autogalaxy_profiling) |" in md
    assert board.headline(views) == "2 projects · 13 records · 0 cached"
    assert set(board.markers(md)) == {"lens", "galaxy"}
    state = board.render_state(views, NOW, NOW)
    assert state["organ"] == "pulse" and state["repo"] == "PyAutoPulse"
    assert state["pages_url"] == "https://pyautolabs.github.io/PyAutoPulse/"
    assert _validator().validate_state(state) == []


def test_render_is_deterministic(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "lens_summary_v1.json")
    board.write([s], tmp_path, now=NOW)
    first = {p.name: p.read_bytes() for p in tmp_path.glob("*.*") if p.is_file()}
    board.write([s], tmp_path, now=NOW)
    assert {p.name: p.read_bytes() for p in tmp_path.glob("*.*") if p.is_file()} == first
    fresh = ingest.ingest(lens, tmp_path, now="2026-10-03T00:00:00Z")
    board.write([fresh], tmp_path, now=NOW)
    after = {p.name: p.read_bytes() for p in tmp_path.glob("*.*") if p.is_file()}
    assert after["state.json"] == first["state.json"]
    assert after["dashboard.md"] == first["dashboard.md"]
    assert after["dashboard.html"] != first["dashboard.html"]
    normalize = board.setup_browser.theme().normalize_refresh_stamp
    assert normalize(after["dashboard.html"].decode()) == normalize(
        first["dashboard.html"].decode()
    )


def test_no_league_table_across_projects(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "lens_summary_v1.json")
    md = board.render_markdown([s], NOW).lower()
    for word in ("fastest", "slowest", "league table", "winner", "verdict:", "release-ready"):
        assert word not in md
    html = board.render_html([s], NOW)
    assert "<title>PyAutoPulse dashboard</title>" in html and "data-refreshed-at=" in html


def test_capture_freshness_is_conservative(lens, web, tmp_path):
    s = _view(lens, web, tmp_path, "lens_summary_v1.json")
    html = board.render_html([s])
    assert 'data-refreshed-at="' + s.refreshed_at + '"' in html
    assert (
        "https://github.com/PyAutoLabs/PyAutoPulse/actions/workflows/dashboard_refresh.yml" in html
    )
    s.outcome = "unavailable"
    s.cached = True
    assert "Last updated unavailable" in board.render_html([s])
    s.outcome = "ok"
    s.refreshed_at = None
    assert "Last updated unavailable" in board.render_html([s])


# ------------------------------------------- v3 lifecycle and walltime axis ---


def _snapshot(name, schema, fixture):
    from pulse.ingest import Snapshot
    from pulse.registry import Instance

    instance = Instance(
        name,
        "autolens_profiling" if name == "lens" else "autolens_inference",
        "dashboard/catalogue.json",
        schema,
        "https://example.invalid",
        github="PyAutoLabs/autolens_profiling",
    )
    return Snapshot(instance, "ok", "remote", fixture_doc(fixture), SHA_A, NOW, refreshed_at=NOW)


def test_v3_status_lines_carry_lifecycle_counts():
    s = _snapshot("lens", "profiling-summary@3", "setup_summary_v3.json")
    expected = "5 current · 1 superseded · 3 archived (producer-declared)"
    assert board.lifecycle(s) == expected
    md = board.render_markdown([s], NOW, campaign_data={"campaigns": [], "tasks": []})
    assert f"- **Lifecycle:** {expected}" in md
    assert "current runtime setups" in md
    assert "| imaging | delaunay | hst | standard | `jax_gpu_dense` |" in md
    assert "imaging-delaunay-hst-a100-runtime-old" not in md
    assert "Coverage: 1 optimal cell(s) not measured." in md
    state = board.render_state([s], updated=NOW, now=NOW)
    census = next(i for i in state["items"] if i["id"] == "pulse:lens:census")
    assert expected in census["text"]


def test_v2_status_lines_are_unchanged():
    s = _snapshot("lens", "profiling-summary@2", "setup_summary_v2.json")
    assert board.lifecycle(s) is None
    md = board.render_markdown([s], NOW, campaign_data={"campaigns": [], "tasks": []})
    assert "**Lifecycle:**" not in md


def test_profiling_and_inference_timings_open_per_project():
    lens = _snapshot("lens", "profiling-summary@3", "setup_summary_v3.json")
    wall = _snapshot("lens-walltime", "walltime-validation@1", "walltime_validation_v1.json")
    data = {"campaigns": [], "tasks": []}
    page = board.render_html([lens, wall], NOW, campaign_data=data)
    assert 'id="evidence"' in page  # old links still land
    profiling = page.index('id="profiling-timings"')
    inference = page.index('id="inference-timings"')
    assert profiling < page.index('id="profiling-pyautolens"') < inference
    assert (
        inference < page.index('id="inference-pyautofit"') < page.index('id="inference-pyautolens"')
    )
    assert inference < page.index('data-walltime="lens-walltime"')
    assert board.INSIGHT_URL in page and ">Profiling Results</h2>" not in page
    assert '"#profiling-timings"' in page and '"#inference-timings"' in page
    assert "setup catalogue unavailable" not in page
    md = board.render_markdown([lens, wall], NOW, campaign_data=data)
    assert md.index("## Profiling Timings") < md.index("## Inference Timings")
    assert md.index("## Inference Timings") < md.index("inference timings</summary>")
    state = board.render_state([wall], updated=NOW, now=NOW)
    assert not any(i["id"].endswith(":unqualified") for i in state["items"])
    assert "full-fit records" in board.qualification(wall)


def _inference(page):
    return re.search(r'data-walltime="lens-walltime".*?</section>', page, re.S)[0]


def test_inference_table_is_mass_total_only_with_the_human_columns():
    lens = _snapshot("lens", "profiling-summary@3", "setup_summary_v3.json")
    wall = _snapshot("lens-walltime", "walltime-validation@1", "walltime_validation_v1.json")
    page = board.render_html([lens, wall], NOW, campaign_data={"campaigns": [], "tasks": []})
    table = _inference(page)
    head = re.findall(r"<th(?: [^>]*)?>([^<]*)</th>", table)
    assert head == list(board.WALLTIME_HEAD)
    rows = re.findall(r'<tr data-record="([^"]+)"', table)
    assert "nautilus-source-pix-s1" not in rows and len(rows) == 4
    for clutter in (
        "Full-fit measurements",
        "Predicted",
        "Measured/predicted",
        "Parallel efficiency",
        "Parity",
        "Reference runtime",
        "Release",
        "mass_total",
        "Log Likelihood Function Evaluation Time",
    ):
        assert clutter not in table, clutter
    first = re.search(r'<tr data-record="nautilus-1core-s0".*?</tr>', table, re.S)[0]
    assert 'data-value="nautilus" hidden>nautilus</td>' in first
    assert ">4200.0</b>" in first and ">0.21000</b>" in first
    # Sampler is constant (hidden, named in the caption); lens light and cores differ.
    assert re.search(r'data-id="constant-caption">All rows: nautilus sampler<', table)
    assert re.search(r'<th data-col="sampler"[^>]* hidden>', table)
    assert not re.search(r'<th data-col="(lens_light|cores)"[^>]* hidden>', table)
    assert re.search(r'data-id="tally"[^>]*>4 results<', table)
    assert 'data-filter="history"' not in table and 'data-filter="class"' not in table


def test_inference_profiling_runtime_links_the_profiling_detail_page():
    lens = _snapshot("lens", "profiling-summary@3", "setup_summary_v3.json")
    wall = _snapshot("lens-walltime", "walltime-validation@1", "walltime_validation_v1.json")
    page = board.render_html([lens, wall], NOW, campaign_data={"campaigns": [], "tasks": []})
    table = _inference(page)
    row = lambda rid: re.search(rf'<tr data-record="{rid}".*?</tr>', table, re.S)[0]  # noqa: E731
    linked = row("nautilus-1core-s0")
    assert (
        "href='?view=setup&amp;instance=lens&amp;record=imaging-delaunay-hst-ral-runtime'" in linked
    )
    assert "≠ size" not in linked
    differs = row("nautilus-16core-s0")
    assert "title='inference 784 px vs profiling 1250 px'>≠ size</span>" in differs
    unmatched = row("nautilus-light-fixed-s0")
    assert "title='no profiling runtime record with model_variant light_fixed'>—" in unmatched
    uncaptured = row("nautilus-gpu-s0")
    assert (
        "not in captured catalogue" in uncaptured
        and "data-detail-link href='?view=setup" not in uncaptured
    )
    assert ">default · mixed</td>" in uncaptured and "<code>jax_gpu_dense</code>" in uncaptured
    # Every row opens its own run page, and the linked profiling page exists.
    assert 'data-view="run" data-instance="lens-walltime" data-record="nautilus-gpu-s0"' in page
    assert (
        'data-view="setup" data-instance="lens" data-record="imaging-delaunay-hst-ral-runtime"'
        in page
    )
    md = board.render_markdown([lens, wall], NOW, campaign_data={"campaigns": [], "tasks": []})
    assert (
        f"[**0.21000**]({board.PAGES_URL}?view=setup&instance=lens&record="
        "imaging-delaunay-hst-ral-runtime)" in md
    )


def test_v3_and_walltime_state_meets_the_brain_contract():
    lens = _snapshot("lens", "profiling-summary@3", "setup_summary_v3.json")
    wall = _snapshot("lens-walltime", "walltime-validation@1", "walltime_validation_v1.json")
    state = board.render_state([lens, wall], updated=NOW, now=NOW)
    assert _validator().validate_state(state) == []
