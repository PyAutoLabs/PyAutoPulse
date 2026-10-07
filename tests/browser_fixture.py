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
