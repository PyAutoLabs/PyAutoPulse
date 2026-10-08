"""Emit a hermetic multi-project board and exact hashed shard for Chromium."""

import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pulse import board  # noqa: E402
from pulse.ingest import Snapshot  # noqa: E402
from pulse.registry import Instance  # noqa: E402


def write(destination):
    destination.mkdir(parents=True, exist_ok=True)
    doc = json.loads((Path(__file__).parent / "fixtures/setup_summary_v2.json").read_text())
    doc["setups"][0]["evidence"] = {"path": "results/fixture.json", "fragment": "/"}
    doc["navigation"] = []
    shard = json.dumps(doc).encode()
    filename = "catalogue/shards/" + "a" * 20 + ".json"
    doc["evidence_shards"] = [
        {
            "setup_id": doc["setups"][0]["id"],
            "path": filename,
            "sha256": hashlib.sha256(shard).hexdigest(),
            "records": len(doc["records"]),
        }
    ]
    path = destination / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(shard)
    snapshots = []
    for name in ("lens", "galaxy"):
        instance = Instance(
            name,
            "auto" + name + "_profiling",
            "dashboard/catalogue.json",
            "profiling-summary@2",
            "https://example.invalid",
            github="PyAutoLabs/auto" + name + "_profiling",
        )
        snapshots.append(
            Snapshot(instance, "ok", "remote", copy.deepcopy(doc), "b" * 40, "2026-10-05T00:00:00Z")
        )
    (destination / "index.html").write_text(board.render_html(snapshots))
    inline = copy.deepcopy(snapshots[0])
    inline.doc.pop("evidence_shards")
    inline.doc.pop("navigation")
    (destination / "inline.html").write_text(board.render_html([inline]))

    headlines = copy.deepcopy(inline)
    base_setup = headlines.doc["setups"][0]
    base_setup["configuration"]["vmap_batch_size"] = {"value": 16, "unit": "count"}
    base_row = headlines.doc["records"][0]
    for metric, value, axis, unit in [
        ("vmap.per_call", 0.005, "runtime", "s"),
        ("device_peak_allocated", 2_000_000_000, "memory", "B"),
    ]:
        row = copy.deepcopy(base_row)
        row.update(id=metric, metric=metric, axis=axis, unit=unit, measurement={metric: value})
        headlines.doc["records"].append(row)
    # Same configuration, different device: the selector must replace all values.
    for original in list(headlines.doc["records"]):
        row = copy.deepcopy(original)
        row["id"] += "-gpu"
        row["identity"]["device"] = "gpu"
        row["measurement"][row["metric"]] *= 2
        headlines.doc["records"].append(row)
    # A distinct compile-only setup remains a distinct selectable configuration.
    compile_setup = copy.deepcopy(base_setup)
    compile_setup["id"] = "compile-only"
    compile_setup["evidence"]["path"] = "results/compile/jax.json"
    headlines.doc["setups"].append(compile_setup)
    compile_row = copy.deepcopy(base_row)
    compile_row.update(
        id="compile-only-row",
        setup_id="compile-only",
        axis="compile",
        metric="full_pipeline.compile",
        measurement={"full_pipeline.compile": 7},
    )
    headlines.doc["records"].append(compile_row)
    other_instrument = copy.deepcopy(base_setup)
    other_instrument.update(id="euclid-fixture", instrument="euclid")
    headlines.doc["setups"].append(other_instrument)
    other_row = copy.deepcopy(base_row)
    other_row.update(
        id="euclid-runtime", setup_id=other_instrument["id"], measurement={"single_call": 0.25}
    )
    headlines.doc["records"].append(other_row)
    (destination / "headlines.html").write_text(board.render_html([headlines]))

    # Two verified shards with delayed transport exercise rapid selection changes.
    async_headlines = copy.deepcopy(headlines)
    async_headlines.doc["evidence_shards"] = []
    for index, setup in enumerate(headlines.doc["setups"]):
        detail = copy.deepcopy(headlines.doc)
        detail["setups"] = [setup]
        detail["records"] = [r for r in detail["records"] if r["setup_id"] == setup["id"]]
        raw = json.dumps(detail).encode()
        name = "catalogue/shards/" + str(index + 1) * 20 + ".json"
        (destination / name).write_bytes(raw)
        async_headlines.doc["evidence_shards"].append(
            {
                "setup_id": setup["id"],
                "path": name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "records": len(detail["records"]),
            }
        )
    (destination / "async-headlines.html").write_text(board.render_html([async_headlines]))

    grouped = copy.deepcopy(inline)
    record = grouped.doc["records"][0]
    grouped.doc["records"] = []
    for metric, value, statistic in [
        ("single_call", 1, "median"),
        ("single_call", 2, "mean"),
        ("batch_wall", 10, "median"),
        ("batch_per_call", 0.5, "median"),
    ]:
        row = copy.deepcopy(record)
        row.update(
            id=metric + statistic,
            axis="runtime",
            metric=metric,
            unit="s",
            measurement={metric: value},
        )
        row["method"]["statistic"] = statistic
        grouped.doc["records"].append(row)
    (destination / "grouping.html").write_text(board.render_html([grouped]))

    scaled = copy.deepcopy(inline)
    component = copy.deepcopy(scaled.doc["records"][1])
    component["id"] = "second-component"
    component["metric"] = "inversion.jit.steady_per_call_s"
    component["measurement"] = {"inversion.jit.steady_per_call_s": 0.01}
    component["method"]["id"] = "different-component-method-id"
    scaled.doc["records"].append(component)
    runtime = copy.deepcopy(scaled.doc["records"][0])
    runtime["id"] = "runtime-second-observation"
    runtime["run_id"] = "second-repeat"
    runtime["measurement"] = {"single_call": 0.025}
    scaled.doc["records"].append(runtime)
    (destination / "scaling.html").write_text(board.render_html([scaled]))

    readable = copy.deepcopy(inline)
    readable.doc["records"] = []
    original = inline.doc["records"][1]
    for metric, value in [
        ("steps.Regularized reconstruction", 0.03),
        ("setup_prefix_8.jit.steady_per_call_s", 0.2),
        ("steps.Data vector (D)", 0.01),
        ("component_total", 0.1),
        ("steps.Curvature matrix (F)", 0.05),
        ("reconstruction.jit.steady_per_call_s", 0.03),
    ]:
        row = copy.deepcopy(original)
        row.update(id=metric, metric=metric, measurement={metric: value})
        row["identity"]["backend"] = "cpu"
        readable.doc["records"].append(row)
    readable.doc["navigation"] = [
        {
            "dataset": "imaging",
            "model": "delaunay",
            "category": "scientific_entrypoint",
            "path": "scripts/imaging/delaunay/likelihood_runtime" + suffix + ".py",
        }
        for suffix in ("", "_numba")
    ]
    numba = copy.deepcopy(readable.doc["setups"][0])
    numba["id"] = "numba-cpu"
    numba["evidence"]["path"] = "results/delaunay_numba.json"
    readable.doc["setups"].append(numba)
    numba_row = copy.deepcopy(inline.doc["records"][0])
    numba_row.update(
        id="numba-runtime",
        setup_id=numba["id"],
        metric="direct_call",
        measurement={"direct_call": 0.4},
    )
    numba_row["identity"]["backend"] = "cpu"
    numba_row["evidence"] = numba["evidence"]
    readable.doc["records"].append(numba_row)
    (destination / "readable.html").write_text(board.render_html([readable]))

    menu = copy.deepcopy(readable)
    for model in ("mge_mass", "knn", "mge", "rectangular"):
        for suffix in ("", "_numba"):
            menu.doc["navigation"].append(
                {
                    "dataset": "imaging",
                    "model": model,
                    "category": "scientific_entrypoint",
                    "path": f"scripts/imaging/{model}/likelihood_runtime{suffix}.py",
                }
            )
    menu.doc["navigation"].append(
        {
            "dataset": "imaging",
            "model": "delaunay",
            "category": "scientific_entrypoint",
            "path": "scripts/imaging/delaunay/unknown.py",
        }
    )
    menu.doc["navigation"].append(
        {
            "dataset": "imaging",
            "model": "sersic",
            "category": "scientific_entrypoint",
            "path": "scripts/imaging/sersic/latent_magnification.py",
        }
    )
    (destination / "menu-order.html").write_text(board.render_html([menu]))

    isolated = copy.deepcopy(readable)
    isolated.doc["records"] = [
        r for r in isolated.doc["records"] if r["metric"] != "component_total"
    ]
    for row in isolated.doc["records"]:
        if row["metric"] == "reconstruction.jit.steady_per_call_s":
            row["run_id"] = "independent-probe"
    (destination / "diagnostic-isolation.html").write_text(board.render_html([isolated]))

    filtered = copy.deepcopy(inline)
    original_setup = filtered.doc["setups"][0]
    original_records = copy.deepcopy(filtered.doc["records"])
    for name, precision, pixels, device in [
        ("archived-float32", "float32", 1500, "cpu"),
        ("archived-3000", "float64", 3000, "cpu"),
        ("archived-a100", "float32", 1500, "a100"),
    ]:
        setup = copy.deepcopy(original_setup)
        setup["id"] = name
        setup["configuration"]["source_pixels"]["value"] = pixels
        filtered.doc["setups"].append(setup)
        for original in original_records:
            record = copy.deepcopy(original)
            record["setup_id"] = name
            record["id"] += name
            record["identity"]["precision"] = precision
            record["identity"]["device"] = device
            filtered.doc["records"].append(record)
    (destination / "filtering.html").write_text(board.render_html([filtered]))

    real = json.loads((Path(__file__).parent / "fixtures/browser_measurements.json").read_text())
    for name, text in real["shards"].items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    captured = copy.deepcopy(snapshots[0])
    captured.doc = real["catalogue"]
    captured.commit = real["capture_commit"]
    (destination / "measurements.html").write_text(board.render_html([captured]))
    legacy = copy.deepcopy(captured)
    for manifest in legacy.doc["evidence_shards"]:
        manifest.pop("axis_devices", None)
    (destination / "legacy-devices.html").write_text(board.render_html([legacy]))
    for manifest in legacy.doc["evidence_shards"]:
        manifest.pop("axes", None)
    legacy.doc["records"] = []
    (destination / "unknown-axes.html").write_text(board.render_html([legacy]))


if __name__ == "__main__":
    write(Path(sys.argv[1]))
