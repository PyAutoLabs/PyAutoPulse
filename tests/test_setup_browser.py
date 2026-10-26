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


# ------------------------------------------------ v3: Class-first browser ---


def lifecycle_capture():
    snapshot = capture()
    return replace(snapshot, doc=fixture_doc("setup_summary_v3.json"))


def test_v3_first_select_is_class_with_all_selected():
    page = setup_browser.render(lifecycle_capture())
    selects = re.findall(r"<select[^>]*data-filter=\"([a-z_]+)\"[^>]*>(.*?)</select>", page, re.S)
    assert [key for key, _ in selects] == [
        "class",
        "dataset_type",
        "variant",
        "instrument",
        "host_class",
    ]
    options = re.findall(r'<option value="([a-z]+)"( selected)?>', selects[0][1])
    assert options == [
        ("all", " selected"),
        ("optimal", ""),
        ("secondary", ""),
        ("experimental", ""),
    ]
    assert 'data-filter="history"' in page and "checked" not in page
    assert "data-view" not in page and "Measurement" not in page


def test_v3_table_is_runtime_only_with_the_human_columns():
    page = setup_browser.render(lifecycle_capture())
    head = re.findall(r"<th(?: [^>]*)?>(.*?)</th>", page)
    assert head[:10] == [
        "Dataset type",
        "Model",
        "Instrument",
        "Regime",
        "Setup",
        "Hardware class",
        "Model variant",
        "Runtime s",
        "Est. 12-core s",
        "Class",
    ]
    rows = dict(re.findall(r'<tr data-record="([^"]+)"[^>]*?( hidden)?>', page))
    assert "imaging-delaunay-hst-a100-breakdown" not in rows  # runtime only
    assert rows["imaging-delaunay-hst-a100-runtime"] == ""
    assert rows["imaging-delaunay-hst-ral-runtime"] == ""  # default class: All
    assert rows["imaging-delaunay-hst-a100-mixed"] == ""
    assert rows["imaging-delaunay-hst-a100-runtime-old"] == " hidden"  # superseded
    assert 'data-status="archived"' not in page


def _row(page, rid):
    return re.search(rf'<tr data-record="{rid}".*?</tr>', page, re.S)[0]


def test_v3_runtime_is_the_producer_vmap_per_call_in_bold_5dp():
    doc = lifecycle_capture().doc
    ral = next(r for r in doc["records"] if r["id"] == "imaging-delaunay-hst-ral-runtime")
    page = setup_browser.render(lifecycle_capture())
    row = _row(page, "imaging-delaunay-hst-ral-runtime")
    cells = re.findall(r"<td class='num'>(.*?)</td>", row)
    expected = f"{ral['projected_node_throughput']['per_call_s']:.5f}"
    assert f">{expected}</b>" in cells[0]
    assert f">{ral['estimated_12_core']['value_s']:.5f}</b>" in cells[1]
    assert "single_jit" not in row and "(single_call)" not in row
    a100 = _row(page, "imaging-delaunay-hst-a100-runtime")
    assert "numba CPU setups only" in re.findall(r"<td class='num'>(.*?)</td>", a100)[1]


def test_v3_setup_drops_precision_only_and_precision_becomes_a_variant():
    assert setup_browser.setup_label("jax_gpu_sparse_fp64") == "jax_gpu_sparse"
    assert setup_browser.setup_label("numba_cpu_sparse_fp64_wtilde") == "numba_cpu_sparse_wtilde"
    assert setup_browser.setup_label("jax_gpu_sparse_mixed_wtilde") == "jax_gpu_sparse_wtilde"
    assert setup_browser.variant_label("default", "jax_gpu_dense_fp64") == "default"
    assert setup_browser.variant_label("default", "jax_gpu_dense_mixed") == "default+mixed"
    assert setup_browser.variant_label("light_fixed", "x_fp32") == "light_fixed+fp32"
    page = setup_browser.render(lifecycle_capture())
    mixed = _row(page, "imaging-delaunay-hst-a100-mixed")
    assert "<code>jax_gpu_dense</code>" in mixed and "<td>default+mixed</td>" in mixed


def test_v3_tally_counts_current_results_and_clutter_is_gone():
    page = setup_browser.render(lifecycle_capture())
    tally = re.search(r'data-id="tally"[^>]*>([^<]*)<', page)[1]
    assert tally == "4 results"
    assert page.index('data-id="tally"') < page.index('data-filter="history"')
    for clutter in ("superseded (shown with History)", "ranks nothing", "decision rules"):
        assert clutter not in page


def test_v3_every_row_opens_its_detail_page():
    page = setup_browser.render(lifecycle_capture())
    row = _row(page, "imaging-delaunay-hst-a100-runtime")
    href = re.search(r'class="row-open" data-detail-link href="([^"]+)"', row)[1]
    assert href == "?view=setup&amp;instance=lens&amp;record=imaging-delaunay-hst-a100-runtime"


def test_v3_coverage_lists_optimal_cells_without_a_current_record():
    page = setup_browser.render(lifecycle_capture())
    coverage = re.search(r'data-id="coverage">(.*?)</details>', page, re.S)[1]
    assert "1 optimal cell not measured" in coverage
    assert "euclid" in coverage and "numba_cpu_sparse_fp64" not in coverage
    assert setup_browser.not_measured(lifecycle_capture().doc)[0]["instrument"] == "euclid"


def test_v3_bypasses_the_v2_payload_and_heuristics():
    page = setup_browser.render(lifecycle_capture())
    assert "setup-payload" not in page and "data-lifecycle" in page
    v2 = setup_browser.render(capture())
    assert "data-lifecycle" not in v2 and "setup-payload" in v2


def test_v3_node_throughput_is_described_with_its_basis():
    doc = lifecycle_capture().doc
    ral = next(r for r in doc["records"] if r["id"] == "imaging-delaunay-hst-ral-runtime")
    kind, text, detail = setup_browser.node_throughput(ral)
    assert kind == "projected"
    assert text == "190.5 calls/s · 40 workers (memory-bound) on ral_cpu_node"
    for needle in (
        "Projected, not measured",
        "η (parallel efficiency) 1 (upper bound)",
        "Bound by memory (worker caps: cores 236, memory 40)",
        "warm_iid_median_s",
    ):
        assert needle in detail, (needle, detail)
    sma = next(r for r in doc["records"] if r["id"] == "interferometer-mge-sma-ral-runtime")
    assert setup_browser.node_throughput(sma)[1].startswith("not projected: peak_rss_gb not")


def test_v3_markdown_shows_the_runtime_table():
    lines = "\n".join(setup_browser.markdown(lifecycle_capture()))
    assert "| Runtime s | Est. 12-core s | Class |" in lines
    assert "| imaging | delaunay | hst | standard | `jax_gpu_dense` | hpc_a100 | default |" in lines
    assert "imaging-delaunay-hst-a100-runtime-old" not in lines


def test_v3_links_the_knowledge_page_under_extra_information():
    from pulse import ORGAN_ROOT

    assert setup_browser.KNOWLEDGE_URL.endswith(
        "/blob/main/knowledge/cpu_parallel_vs_gpu_batched.md"
    )
    page_path = ORGAN_ROOT / "knowledge/cpu_parallel_vs_gpu_batched.md"
    assert page_path.read_text().startswith(f"# {setup_browser.KNOWLEDGE_TITLE}\n")
    page = setup_browser.render(lifecycle_capture())
    assert page.index("Extra Information") < page.index('data-id="knowledge-link"')
    link = re.search(r'data-id="knowledge-link">(.*?)</p>', page, re.S)[1]
    assert f'href="{setup_browser.KNOWLEDGE_URL}"' in link and 'target="_blank"' in link
    assert f">{setup_browser.KNOWLEDGE_TITLE}</a>" in link
    markdown = "\n".join(setup_browser.markdown(lifecycle_capture()))
    assert f"[{setup_browser.KNOWLEDGE_TITLE}]({setup_browser.KNOWLEDGE_URL})" in markdown


# ------------------------------------------- v3: per-row detail pages ---


def _article(pages, rid):
    return re.search(
        rf'<article class="detail-page"[^>]*data-record="{rid}".*?</article>', pages, re.S
    )[0]


def test_v3_detail_page_per_runtime_row_restores_the_full_breakdown():
    pages = setup_browser.detail_pages(lifecycle_capture(), "#profiling-pyautolens", "PyAutoLens")
    ids = re.findall(r'<article class="detail-page"[^>]*data-record="([^"]+)"', pages)
    assert sorted(ids) == sorted(
        r["id"] for r in setup_browser.runtime_rows(lifecycle_capture().doc)
    )
    assert pages.count("<article") == pages.count(" hidden>")
    a100 = _article(pages, "imaging-delaunay-hst-a100-runtime")
    assert (
        "<h2>PyAutoLens / imaging / delaunay / hst / jax_gpu_dense / hpc_a100 / default</h2>"
        in a100
    )
    breakdown = re.search(r'data-axis="breakdown".*?</details>', a100, re.S)[0]
    for metric in ("component_total", "mapping", "inversion"):
        assert f"data-metric='{metric}'" in breakdown
    assert "width:100.0%" in breakdown  # component_total is the scale
    assert 'href="#profiling-pyautolens"' in a100 and "← Profiling Timings" in a100
    # History lists the superseded runtime on the same key as a link to its own page.
    history = re.search(r'data-axis="history".*?</details>', a100, re.S)[0]
    assert "record=imaging-delaunay-hst-a100-runtime-old" in history
    assert "(this page)" in history


def test_v3_detail_page_carries_twelve_core_node_throughput_and_status():
    pages = setup_browser.detail_pages(lifecycle_capture(), "#x", "PyAutoLens")
    ral = _article(pages, "imaging-delaunay-hst-ral-runtime")
    assert "Est. 12-core" in ral and "0.03500 s" in ral
    assert "190.5 calls/s · 40 workers (memory-bound) on ral_cpu_node" in ral
    assert "projected-badge" in ral and "Projected, not measured" in ral
    for label in ("Class", "Status", "Decision", "Configuration", "Evidence"):
        assert label in ral
    assert "single_call" in ral
    # The superseded page shows only superseded siblings (none here), never current ones.
    old = _article(pages, "imaging-delaunay-hst-a100-runtime-old")
    assert "data-metric='mapping'" not in old


def test_v3_detail_pages_sit_in_the_hidden_route_container():
    page = board.render_html([lifecycle_capture()], campaign_data={"campaigns": [], "tasks": []})
    container = page.index('id="detail-pages"')
    assert container < page.index('id="profiling-timings"')
    assert 'id="detail-pages" hidden' in page and 'id="detail-route-status"' in page
    assert setup_browser.page_ids(lifecycle_capture()) >= {"imaging-delaunay-hst-a100-runtime"}


def test_rows_are_ordered_by_likelihood_instrument_setup_hardware_variant():
    rows = setup_browser.runtime_rows(lifecycle_capture().doc)
    keys = [setup_browser.row_order(r) for r in rows]
    assert keys == sorted(keys)
    assert rows[0]["likelihood"]["dataset_type"] == "imaging"
    assert rows[-1]["likelihood"]["dataset_type"] == "interferometer"


def test_setup_label_drops_an_na_operator_token():
    assert setup_browser.setup_label("jax_cpu_na_fp64") == "jax_cpu"
    assert setup_browser.setup_label("jax_gpu_na_fp64") == "jax_gpu"


def test_breakdown_shows_one_entry_per_labelled_step():
    record = {
        "status": "current",
        "unit": "s",
        "values": {
            "component_total": 0.1,
            "steps.Regularized reconstruction": 0.03,
            "reconstruction_jit.steady_per_call_s": 0.03,
            "steps.Curvature matrix (F)": 0.05,
            "curvature_matrix_sparse_jit.steady_per_call_s": 0.05,
            "interpolator_prefix": 0.008,
        },
    }
    panel = setup_browser._metric_panel([record], "Likelihood breakdown", "breakdown")
    main, rest = panel.split("data-id='recorded-keys'")
    assert "data-metric='steps.Regularized reconstruction'" in main
    assert "reconstruction_jit" not in panel and "curvature_matrix_sparse_jit" not in panel
    assert "data-metric='interpolator_prefix'" in rest and "interpolator_prefix" not in main
    assert "All recorded keys (1 without a labelled step)" in rest
    assert "width:30.0%" in main  # scaled to component_total


def test_a_raw_key_is_dropped_only_as_the_unambiguous_twin_of_one_step():
    values = {
        "component_total": 1.0,
        "steps.Data vector (D)": 0.2,
        "data_vector_jit.steady_per_call_s": 0.2,  # the one twin
        "steps.Lens light images": 0.0,
        "psf_weighted_data_jit.steady_per_call_s": 0.0,  # unrelated, same value
        "steps.Ray-trace mesh grid": 0.3,
        "ray_trace_mesh_jit.steady_per_call_s": 0.3,
        "ray_trace_mesh_prefix": 0.3,  # several raw keys share 0.3: ambiguous
        "steps.Curvature matrix (F)": 0.4,
        "steps.Regularization matrix (H)": 0.4,  # several steps share 0.4
        "curvature_matrix_jit.steady_per_call_s": 0.4,
    }
    assert setup_browser.step_twins(values) == {"data_vector_jit.steady_per_call_s"}


def test_superseded_pages_show_only_siblings_tied_to_the_same_run():
    def rec(rid, measurement, status, run, path, day="2026-09-08"):
        return {
            "id": rid,
            "measurement": measurement,
            "status": status,
            "run_id": run,
            "evidence": {"path": path},
            "measured_at": f"{day}T00:00:00Z",
        }

    row = rec("r", "runtime", "superseded", "run-a", "results/x/exp1/runtime.json")
    same_dir = rec("b1", "breakdown", "superseded", "run-b", "results/x/exp1/breakdown.json")
    same_run = rec("c1", "compile", "superseded", "run-a", "results/x/exp1/runtime.json")
    other = rec("b2", "breakdown", "superseded", "run-c", "results/x/exp2/breakdown.json")
    current = rec("b3", "breakdown", "current", "run-d", "results/x/breakdown.json")
    siblings = [row, same_dir, same_run, other, current]
    assert setup_browser.tied_siblings(row, siblings) == [same_dir, same_run]
    now = rec("n", "runtime", "current", "run-e", "results/x/runtime.json")
    assert setup_browser.tied_siblings(now, [now, current, other]) == [current]
    pages = setup_browser.detail_pages(lifecycle_capture(), "#x", "PyAutoLens")
    old = _article(pages, "imaging-delaunay-hst-a100-runtime-old")
    assert "No sibling measurements tied to this run" in old
    assert "No sibling measurements" not in _article(pages, "imaging-delaunay-hst-a100-runtime")


def test_a_shared_directory_ties_only_records_from_the_same_day():
    def rec(rid, measurement, run, day):
        return {
            "id": rid,
            "measurement": measurement,
            "status": "superseded",
            "run_id": run,
            "evidence": {"path": f"results/x/history/{measurement}.json"},
            "measured_at": f"{day}T00:00:00Z",
        }

    row = rec("r", "runtime", "run-a", "2026-09-08")
    same_day = rec("b1", "breakdown", "run-b", "2026-09-08")
    older = rec("b2", "breakdown", "run-c", "2026-07-11")
    assert setup_browser.tied_siblings(row, [row, same_day, older]) == [same_day]
    assert setup_browser.tied_siblings(row, [row, older]) == []
