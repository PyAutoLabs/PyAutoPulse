"""The ``profiling-summary`` v1/v2 exchange contracts, as the organ reads them.

The contract is owned by the producer and documented beside it
(``autolens_profiling/dashboard/README.md``, "summary.json — the
profiling-summary v1 read contract": Envelope / Records / Comparisons). This
module dispatches setup-oriented v2 validation to ``pulse.catalogue`` and
validates the **exchange** contract only — known schema/version,
required fields, unique ids, finite numerics, UTC dates, safe evidence paths,
axis/unit consistency — and pairs each producer comparison with its two
records so the board can refuse a pair whose axis or hardware identity
differs. It never judges a timing, never recomputes a ratio and has no
project-specific branch: every producer behind the contract takes the same
code path. Stdlib only; no scientific library is imported.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import datetime

SUPPORTED = {("profiling-summary", 1), ("profiling-summary", 2)}

ENVELOPE = (
    "schema",
    "version",
    "project",
    "scope",
    "generated_at",
    "evidence_updated_at",
    "producer_revision",
    "comparison_policy",
    "coverage",
    "records",
    "comparisons",
    "limitations",
)

# The measurement axis table. A value's unit must belong to its axis: a memory
# value can never enter a seconds series, and vice versa.
AXIS_UNITS = {
    "runtime": {"s"},
    "compile": {"s"},
    "breakdown": {"s"},
    "memory": {"B", "KiB", "MiB", "GiB", "KB", "MB", "GB"},
}
STATUSES = {"drifted", "improved", "flat", "insufficient"}
HARDWARE = ("device", "backend", "precision", "host")

_SHA = re.compile(r"^[0-9a-f]{40}$")


# ------------------------------------------------------------ primitives ---


def parse_utc(value) -> datetime | None:
    """A datetime for an ISO-8601 timestamp that says it is UTC, else None."""
    if not isinstance(value, str):
        return None
    if value.endswith("Z"):
        text = value[:-1] + "+00:00"
    elif value.endswith("+00:00"):
        text = value
    else:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    off = parsed.utcoffset()
    return parsed if off is not None and off.total_seconds() == 0 else None


def _number(value) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _finite_or_null(value) -> bool:
    return value is None or (_number(value) and math.isfinite(value))


def safe_relative_path(value) -> bool:
    """Repo-relative: not absolute, no ``..``, no URL, no backslash."""
    return (
        isinstance(value, str)
        and bool(value)
        and not value.startswith("/")
        and "://" not in value
        and "\\" not in value
        and ".." not in value.split("/")
    )


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


# ------------------------------------------------------------- validation ---


def supported(doc, wanted: tuple[str, int] | None = None) -> str | None:
    """None when the doc's (schema, version) is readable here, else why not.

    ``wanted`` is the registry row's ``supported_schema``; the doc must match
    it *and* be one this reader implements.
    """
    if not isinstance(doc, dict):
        return "summary is not a JSON object"
    got = (doc.get("schema"), doc.get("version"))
    if not isinstance(got[0], str) or type(got[1]) is not int or got not in SUPPORTED:
        known = ", ".join(f"{s}@{v}" for s, v in sorted(SUPPORTED))
        return f"unsupported schema {got[0]!r} version {got[1]!r} (this reader supports {known})"
    if wanted is not None and got != tuple(wanted):
        return f"schema {got[0]}@{got[1]} is not the registered {wanted[0]}@{wanted[1]}"
    return None


def validate(doc) -> list[str]:
    """Validate the versioned contract; unsupported documents fail closed."""
    why = supported(doc)
    if why:
        return [why]
    if doc["version"] == 2:
        from pulse import catalogue

        return catalogue.validate(doc)
    return _validate_v1(doc)


def _validate_v1(doc) -> list[str]:
    """Every exchange-contract break in a parsed summary (empty = valid).

    Schema/version support is checked separately by ``supported``; this
    checks the v1 shape.
    """
    if not isinstance(doc, dict):
        return ["summary is not a JSON object"]
    out = [f"missing required field {k!r}" for k in ENVELOPE if k not in doc]
    for key in ("project", "scope"):
        if key in doc and not _text(doc[key]):
            out.append(f"{key} must be a non-empty string")
    if "generated_at" in doc and parse_utc(doc["generated_at"]) is None:
        out.append(f"generated_at is not an ISO-8601 UTC timestamp: {doc['generated_at']!r}")
    evidence = doc.get("evidence_updated_at")
    if "evidence_updated_at" in doc:
        if evidence is None:
            if not _text(doc.get("evidence_updated_at_reason")):
                out.append("evidence_updated_at is null without evidence_updated_at_reason")
        elif parse_utc(evidence) is None:
            out.append(f"evidence_updated_at is not an ISO-8601 UTC timestamp: {evidence!r}")
    valid_until = doc.get("valid_until")
    if valid_until is not None:
        vu = parse_utc(valid_until)
        if vu is None:
            out.append(f"valid_until is not an ISO-8601 UTC timestamp or null: {valid_until!r}")
        else:
            ev = parse_utc(evidence)
            if ev is not None and vu < ev:
                out.append("valid_until precedes evidence_updated_at")
    rev = doc.get("producer_revision")
    if rev is not None and not (isinstance(rev, str) and _SHA.match(rev)):
        out.append(f"producer_revision is not a 40-hex commit or null: {rev!r}")
    policy = doc.get("comparison_policy")
    if "comparison_policy" in doc and not (isinstance(policy, dict) and _text(policy.get("id"))):
        out.append("comparison_policy must be an object with an id")
    out += _validate_coverage(doc)
    out += _validate_records(doc)
    out += _validate_comparisons(doc)
    lim = doc.get("limitations")
    if "limitations" in doc and not (isinstance(lim, list) and all(_text(x) for x in lim)):
        out.append("limitations must be a list of non-empty strings")
    return out


def _validate_coverage(doc) -> list[str]:
    if "coverage" not in doc:
        return []
    cov = doc["coverage"]
    if not isinstance(cov, dict):
        return ["coverage is not an object"]
    out = []
    if not isinstance(cov.get("expected"), dict):
        out.append("coverage.expected must be an object")
    obs = cov.get("observed")
    if not isinstance(obs, dict):
        out.append("coverage.observed must be an object")
    else:
        for k, v in obs.items():
            if not (isinstance(v, int) and not isinstance(v, bool) and v >= 0):
                out.append(f"coverage.observed.{k} is not a non-negative integer")
    excluded = cov.get("excluded", [])
    if not isinstance(excluded, list):
        return out + ["coverage.excluded must be a list"]
    for i, x in enumerate(excluded):
        if not isinstance(x, dict):
            out.append(f"coverage.excluded[{i}] is not an object")
            continue
        if not _text(x.get("id")) or not _text(x.get("reason")):
            out.append(f"coverage.excluded[{i}] needs an id and a reason")
        ev = x.get("evidence") if isinstance(x.get("evidence"), dict) else {}
        if not safe_relative_path(ev.get("path")):
            out.append(f"coverage.excluded[{i}] evidence path is not safe: {ev.get('path')!r}")
    return out


def _validate_records(doc) -> list[str]:
    records = doc.get("records")
    if "records" in doc and not isinstance(records, list):
        return ["records is not a list"]
    out = []
    seen: set[str] = set()
    for i, r in enumerate(records or []):
        where = f"records[{i}]"
        if not isinstance(r, dict):
            out.append(f"{where} is not an object")
            continue
        rid = r.get("id")
        if not _text(rid):
            out.append(f"{where} has no id")
        elif rid in seen:
            out.append(f"duplicate record id {rid!r}")
        else:
            seen.add(rid)
            where = f"record {rid!r}"
        axis, unit = r.get("axis"), r.get("unit")
        if axis not in AXIS_UNITS:
            out.append(f"{where}: axis {axis!r} is not one of {', '.join(sorted(AXIS_UNITS))}")
        elif unit not in AXIS_UNITS[axis]:
            out.append(
                f"{where}: unit {unit!r} is not a {axis} unit "
                f"({', '.join(sorted(AXIS_UNITS[axis]))}); a value cannot enter a series "
                "of another unit"
            )
        meas = r.get("measurement")
        if not isinstance(meas, dict) or not meas:
            out.append(f"{where}: measurement must be a non-empty object")
        else:
            if not all(_finite_or_null(v) for v in meas.values()):
                out.append(f"{where}: measurement carries a non-finite or non-numeric value")
            if all(v is None for v in meas.values()):
                out.append(f"{where}: measurement carries no value")
        ident = r.get("identity")
        if not isinstance(ident, dict):
            out.append(f"{where}: identity must be an object")
        else:
            missing = [k for k in ("device", "backend", "precision") if k not in ident]
            if missing:
                out.append(
                    f"{where}: identity lacks {', '.join(missing)} (null + reason if unknown)"
                )
        prov = r.get("provenance")
        if not isinstance(prov, dict):
            out.append(f"{where}: provenance must be an object")
        else:
            for k in ("has_provenance", "qualified"):
                if not isinstance(prov.get(k), bool):
                    out.append(f"{where}: provenance.{k} must be a boolean")
            if "host" not in prov:
                out.append(f"{where}: provenance lacks host (null if unknown)")
            for k, v in prov.items():
                if _number(v) and not math.isfinite(v):
                    out.append(f"{where}: provenance.{k} is non-finite")
        ev = r.get("evidence")
        if not isinstance(ev, dict) or not safe_relative_path(ev.get("path")):
            path = ev.get("path") if isinstance(ev, dict) else None
            out.append(f"{where}: evidence path is not a safe repo-relative path: {path!r}")
    return out


def _validate_comparisons(doc) -> list[str]:
    comparisons = doc.get("comparisons")
    if "comparisons" in doc and not isinstance(comparisons, list):
        return ["comparisons is not a list"]
    policy = doc.get("comparison_policy")
    policy_id = policy.get("id") if isinstance(policy, dict) else None
    out = []
    seen: set[str] = set()
    for i, c in enumerate(comparisons or []):
        where = f"comparisons[{i}]"
        if not isinstance(c, dict):
            out.append(f"{where} is not an object")
            continue
        key = c.get("comparison_key")
        if not _text(key):
            out.append(f"{where} has no comparison_key")
        elif key in seen:
            out.append(f"duplicate comparison_key {key!r}")
        else:
            seen.add(key)
            where = f"comparison {key!r}"
        if c.get("policy") != policy_id:
            out.append(f"{where}: policy {c.get('policy')!r} is not comparison_policy.id")
        if c.get("axis") not in AXIS_UNITS:
            out.append(f"{where}: axis {c.get('axis')!r} is not in the axis table")
        if not _text(c.get("metric")):
            out.append(f"{where}: metric must be a non-empty string")
        if c.get("status") not in STATUSES:
            out.append(f"{where}: status {c.get('status')!r} is not in the contract")
        if not _finite_or_null(c.get("ratio")):
            out.append(f"{where}: ratio is non-finite or non-numeric")
        if not isinstance(c.get("qualified"), bool):
            out.append(f"{where}: qualified must be a boolean")
        reasons = c.get("reasons")
        if not (isinstance(reasons, list) and all(isinstance(x, str) for x in reasons)):
            out.append(f"{where}: reasons must be a list of strings")
        for end in ("baseline", "candidate"):
            v = c.get(end)
            if v is not None and not _text(v):
                out.append(f"{where}: {end} must be a release reference or null")
    return out


def classify(doc, wanted: tuple[str, int] | None = None) -> tuple[str, list[str]]:
    """``(outcome, errors)``: ok | unsupported | invalid."""
    why = supported(doc, wanted)
    if why:
        return "unsupported", [why]
    errors = validate(doc)
    return ("invalid", errors) if errors else ("ok", [])


# ------------------------------------------------------------ comparisons ---


def hardware(record: dict) -> dict:
    """The hardware identity a record was measured on (None = not recorded)."""
    ident = record.get("identity") or {}
    prov = record.get("provenance") or {}
    return {
        "device": ident.get("device"),
        "backend": ident.get("backend"),
        "precision": ident.get("precision"),
        "host": prov.get("host"),
    }


def group_label(hw: dict | None) -> str:
    if hw is None:
        return "unresolved"
    parts = [str(hw[k]) if hw[k] is not None else f"{k} unknown" for k in HARDWARE[:3]]
    return " · ".join(parts)


@dataclass
class Pair:
    """One producer comparison and the records it names, as the board shows it."""

    comparison: dict
    baseline: dict | None = None
    candidate: dict | None = None
    refused: list[str] = field(default_factory=list)
    group: str = "unresolved"

    @property
    def key(self) -> str:
        return self.comparison["comparison_key"]


def _record_id(key: str, ref: str) -> str:
    # The contract's record id grammar: `<series key>@<release reference>`.
    return f"{key}@{ref}"


def pair(doc: dict) -> list[Pair]:
    """Pair every comparison with its baseline/candidate records.

    A pair is **refused** (shown with its reason, its ratio never displayed
    as a comparison) when an endpoint is not among the records, when the two
    records' axes differ from each other or from the comparison's, or when
    their hardware identity (device, backend, precision, host) differs. A host
    is compared only when both records name one: an unrecorded host is
    unknown, not different. Accepted pairs are grouped by hardware identity
    so changed hardware is always a separate group, never merged.
    """
    records = {r["id"]: r for r in doc.get("records") or [] if isinstance(r, dict) and "id" in r}
    by_series: dict[str, dict] = {}
    for rid, r in records.items():
        by_series.setdefault(rid.rpartition("@")[0], r)
    out = []
    for c in doc.get("comparisons") or []:
        p = Pair(c)
        key = c["comparison_key"]
        for end in ("baseline", "candidate"):
            ref = c.get(end)
            if ref is None:
                continue
            rec = records.get(_record_id(key, ref))
            if rec is None:
                p.refused.append(f"{end} record {_record_id(key, ref)!r} is not in records")
            setattr(p, end, rec)
        ends = [r for r in (p.baseline, p.candidate) if r is not None]
        axes = {r.get("axis") for r in ends}
        if len(axes) > 1:
            p.refused.append(
                f"axis mismatch: baseline {p.baseline.get('axis')} vs candidate "
                f"{p.candidate.get('axis')} — never combined"
            )
        elif axes and c.get("axis") not in axes:
            p.refused.append(f"axis mismatch: comparison {c.get('axis')} vs records {axes.pop()}")
        if p.baseline is not None and p.candidate is not None:
            a, b = hardware(p.baseline), hardware(p.candidate)
            changed = [
                k
                for k in HARDWARE
                if a[k] != b[k] and not (k == "host" and (a[k] is None or b[k] is None))
            ]
            if changed:
                diffs = ", ".join(f"{k} {a[k]} → {b[k]}" for k in changed)
                p.refused.append(f"hardware identity changed ({diffs}) — separate groups")
        anchor = p.candidate or p.baseline or by_series.get(key)
        p.group = "refused" if p.refused else group_label(hardware(anchor) if anchor else None)
        out.append(p)
    return out


def qualified_records(doc: dict) -> int:
    """Records the producer marks qualified; unknown provenance never counts."""
    return sum(
        1
        for r in doc.get("records") or []
        if (r.get("provenance") or {}).get("qualified") is True
        and (r.get("provenance") or {}).get("has_provenance") is True
    )
