"""Frozen snapshots: a producer's day-zero baseline, captured once and never rewritten.

``pyauto-pulse freeze --instance lens --label day_zero --commit <sha>`` reads the instance's
``profiling-summary@3`` catalogue at one commit, validates it (decision ids resolved against
this organ's ``decisions.yaml``), keeps the records the producer stamped ``day_zero: <tag>``
(lifecycle report §3.6; autolens_profiling#499) and writes
``snapshots/<label>/<instance>.json``: those records, the catalogue's ``planned_cells`` and a
manifest (source commit, tag, counts, the sha256 of the full catalogue and of the frozen
records). It refuses to overwrite a frozen snapshot: a new baseline is a new label.

``--measurement <m>`` keeps only the stamped records of that measurement and records it in the
snapshot (``measurement``), so a later family of stamps gets its own frozen label without
touching an earlier one: ``freeze --label day_zero_gradient --measurement gradient`` freezes the
phase-6 gradient records while ``day_zero`` keeps the runtime baseline (autolens_profiling#512).

``pyauto-pulse check`` verifies every frozen snapshot offline (``verify``): its manifest
digest still matches its records, every record is ``current`` and carries the snapshot's tag,
and every ``decision_id`` resolves. Pulse selects nothing here: the producer's stamp decides
which records are day zero; Pulse only keeps the capture.

The rolling last-good snapshot (``snapshots/<instance>.json``, ``ingest.py``) is a different
thing: it is overwritten on every good read. A frozen snapshot lives one folder down.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pulse import ORGAN_ROOT, decisions, ingest

SCHEMA = "pulse-frozen-snapshot"
VERSION = 1
_LABEL = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


class FreezeError(ValueError):
    """A freeze that must not be written, or a frozen snapshot that fails verification."""


def frozen_path(out_dir: Path, label: str, instance: str) -> Path:
    return Path(out_dir) / "snapshots" / label / f"{instance}.json"


def _digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()


def _counts(records: list[dict]) -> dict:
    cells = {
        (
            r["likelihood"]["dataset_type"],
            r["likelihood"]["variant"],
            r["instrument"],
            r["setup_id"],
            r["host_class"],
            r.get("model_variant", "default"),
            r.get("regime"),
        )
        for r in records
    }
    by_class = {}
    for r in records:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    return {
        "records": len(records),
        "cells": len(cells),
        "by_class": dict(sorted(by_class.items())),
        "with_decision": sum(1 for r in records if r.get("decision_id")),
    }


def build(
    inst,
    doc: dict,
    raw: bytes,
    commit: str,
    label: str,
    frozen_at: str,
    root=ORGAN_ROOT,
    measurement: str | None = None,
):
    """The frozen snapshot document for one validated v3 catalogue at ``commit``.

    With ``measurement``, only the stamped records of that measurement are kept.
    """
    if not _LABEL.match(label):
        raise FreezeError(f"label {label!r} must be lower_snake_case")
    if not _SHA.match(commit):
        raise FreezeError(f"commit {commit!r} must be a 40-hex SHA")
    outcome, errors = ingest.classify(doc, ("profiling-summary", 3), root)
    if outcome != "ok":
        raise FreezeError(f"{inst.instance}@{commit[:12]} is {outcome}: " + "; ".join(errors[:5]))
    stamped = [
        r
        for r in doc["records"]
        if r.get("day_zero") is not None
        and (measurement is None or r.get("measurement") == measurement)
    ]
    tags = sorted({r["day_zero"] for r in stamped})
    if len(tags) != 1:
        scope = f" {measurement}" if measurement else ""
        raise FreezeError(
            f"{inst.instance}@{commit[:12]}: a frozen snapshot needs exactly one day_zero tag "
            f"on its{scope} records, found {tags or 'none'}"
        )
    records = sorted(stamped, key=lambda r: r["id"])
    snap = {
        "schema": SCHEMA,
        "version": VERSION,
        "label": label,
        "instance": inst.instance,
        "repo": inst.repo,
        "github": inst.github,
        "summary_path": inst.summary_path,
        "commit": commit,
        "frozen_at": frozen_at,
        "tag": tags[0],
        "source": {
            "schema": f"{doc['schema']}@{doc['version']}",
            "generated_at": doc.get("generated_at"),
            "producer_revision": doc.get("producer_revision"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "record_count": len(doc["records"]),
        },
        "counts": _counts(records),
        "decision_ids": sorted({r["decision_id"] for r in records if r.get("decision_id")}),
        "records_sha256": _digest(records),
        "planned_cells": doc.get("planned_cells") or [],
        "records": records,
    }
    if measurement is not None:
        snap["measurement"] = measurement
    return snap


def write(out_dir: Path, snap: dict) -> Path:
    """Write a frozen snapshot once; an existing one is never replaced."""
    path = frozen_path(out_dir, snap["label"], snap["instance"])
    if path.exists():
        raise FreezeError(f"{path} exists: a frozen snapshot is never rewritten (use a new label)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snap, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return path


def freeze(
    inst,
    label: str,
    commit: str,
    out_dir: Path,
    frozen_at: str,
    local=None,
    root=ORGAN_ROOT,
    measurement: str | None = None,
):
    """Fetch ``inst``'s summary at ``commit`` (or read ``local``), build and write the snapshot."""
    if local is not None:
        raw = Path(local).read_bytes()
    else:
        raw = ingest.fetch_at(inst.github, commit, inst.summary_path)
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        raise FreezeError(f"{inst.instance}@{commit[:12]}: unreadable summary ({exc})") from exc
    if frozen_path(out_dir, label, inst.instance).exists():
        raise FreezeError(
            f"{frozen_path(out_dir, label, inst.instance)} exists: a frozen snapshot is never "
            "rewritten (use a new label)"
        )
    return write(out_dir, build(inst, doc, raw, commit, label, frozen_at, root, measurement))


def verify_one(path: Path, known_decisions: set[str]) -> list[str]:
    """Problems with one frozen snapshot (empty when it is intact)."""
    try:
        snap = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return [f"{path}: unreadable ({exc})"]
    where = f"{path.parent.name}/{path.name}"
    if snap.get("schema") != SCHEMA or snap.get("version") != VERSION:
        return [f"{where}: not a {SCHEMA}@{VERSION} document"]
    problems = []
    if snap.get("label") != path.parent.name or snap.get("instance") != path.stem:
        problems.append(f"{where}: label/instance do not match its path")
    records = snap.get("records") or []
    if snap.get("records_sha256") != _digest(records):
        problems.append(f"{where}: records changed since the freeze (records_sha256 mismatch)")
    if snap.get("counts") != _counts(records):
        problems.append(f"{where}: counts do not match its records")
    tag = snap.get("tag")
    off = [r.get("id") for r in records if r.get("day_zero") != tag or r.get("status") != "current"]
    if off:
        problems.append(f"{where}: {len(off)} record(s) not current on tag {tag}, e.g. {off[0]}")
    measurement = snap.get("measurement")
    if measurement is not None:
        other = [r.get("id") for r in records if r.get("measurement") != measurement]
        if other:
            problems.append(
                f"{where}: {len(other)} record(s) not measurement {measurement}, e.g. {other[0]}"
            )
    wanted = {r["decision_id"] for r in records if r.get("decision_id")}
    if sorted(wanted) != snap.get("decision_ids"):
        problems.append(f"{where}: decision_ids do not match its records")
    missing = sorted(wanted - known_decisions)
    if missing:
        problems.append(f"{where}: decision_id(s) not in decisions.yaml: {', '.join(missing[:5])}")
    if not records:
        problems.append(f"{where}: holds no records")
    return problems


def frozen_snapshots(out_dir: Path) -> list[Path]:
    """Every ``snapshots/<label>/<instance>.json`` (the rolling ones sit one level up)."""
    return sorted(p for p in (Path(out_dir) / "snapshots").glob("*/*.json"))


def verify(out_dir: Path, root=ORGAN_ROOT) -> tuple[list[str], list[str]]:
    """(ok lines, problems) for every frozen snapshot under ``out_dir``."""
    paths = frozen_snapshots(out_dir)
    if not paths:
        return [], []
    known = decisions.ids(root)
    ok, problems = [], []
    for path in paths:
        found = verify_one(path, known)
        if found:
            problems += found
            continue
        snap = json.loads(path.read_text())
        counts = snap["counts"]
        ok.append(
            f"{snap['label']}/{snap['instance']}: tag {snap['tag']}, {counts['records']} records "
            f"over {counts['cells']} cells at {snap['commit'][:12]}, "
            f"{len(snap['decision_ids'])} decision(s) resolved"
        )
    return ok, problems
