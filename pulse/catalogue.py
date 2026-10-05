"""Validate the setup-oriented v2 exchange contract without judging evidence.

Stable setup IDs decouple scientific navigation from script paths. Selections
name exact records and their measurement context; missing cells remain explicit.
This module is stdlib-only and does not read files, choose results or compute
comparisons. See REFERENCE.md for the producer-facing grammar.
"""

from __future__ import annotations

import json
import math

from pulse import summary

SELECTION_STATES = {"accepted", "unreviewed", "not_measured", "failed", "unusable", "inapplicable"}
VALIDATION_STATES = {"accepted", "unreviewed", "rejected"}
MEMORY_METRICS = {"host_peak_rss", "device_peak_allocated", "device_peak_reserved", "device_total"}


class _Check:
    def __init__(self):
        self.errors: list[str] = []

    def require(self, condition, where, message):
        if not condition:
            self.errors.append(f"{where}: {message}")

    def text(self, value, where):
        self.require(summary._text(value), where, "must be a non-empty string")

    def choice(self, value, choices, where):
        self.require(
            isinstance(value, str) and value in choices, where, f"must be one of {sorted(choices)}"
        )

    def objects(self, value, where):
        if not isinstance(value, list):
            self.errors.append(f"{where}: must be a list")
            return []
        result = []
        for i, item in enumerate(value):
            if isinstance(item, dict):
                result.append(item)
            else:
                self.errors.append(f"{where}[{i}]: must be an object")
        return result

    def index(self, value, where):
        result = {}
        for i, item in enumerate(self.objects(value, where)):
            key = item.get("id")
            self.text(key, f"{where}[{i}].id")
            if summary._text(key):
                self.require(key not in result, where, f"duplicate id {key!r}")
                result[key] = item
        return result

    def reference(self, value, index, where):
        self.require(
            isinstance(value, str) and value in index, where, f"unknown reference {value!r}"
        )
        return index.get(value) if isinstance(value, str) else None

    def references(self, value, index, where, nonempty=True):
        if not isinstance(value, list):
            self.errors.append(f"{where}: must be a list of references")
            return []
        self.require(bool(value) or not nonempty, where, "must not be empty")
        result = []
        seen = set()
        for item in value:
            record = self.reference(item, index, where)
            if isinstance(item, str):
                self.require(item not in seen, where, f"duplicate reference {item!r}")
                seen.add(item)
            if record is not None:
                result.append(record)
        return result

    def evidence(self, value, where):
        if not isinstance(value, dict):
            self.errors.append(f"{where}: must be an evidence object")
            return
        self.require(summary.safe_relative_path(value.get("path")), where, "unsafe evidence path")
        self.require(
            value.get("fragment") is None or summary._text(value["fragment"]),
            where,
            "invalid evidence fragment",
        )

    def nullable(self, obj, key, where, predicate=summary._text):
        self.require(key in obj, where, f"missing {key}")
        value = obj.get(key)
        if value is None:
            unknowns = obj.get("unknowns")
            self.require(
                isinstance(unknowns, dict) and summary._text(unknowns.get(key)),
                where,
                f"{key} is null without an unknowns reason",
            )
        else:
            self.require(predicate(value), where, f"invalid {key}")

    def validation(self, value, where):
        if not isinstance(value, dict):
            self.errors.append(f"{where}: must be a validation object")
            return None
        self.choice(value.get("status"), VALIDATION_STATES, where)
        self.text(value.get("reason"), f"{where}.reason")
        return value.get("status")


def _finite(value):
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _json_values(check, value, where):
    """Reject non-finite and non-JSON metadata, including nested extensions."""
    if isinstance(value, dict):
        for key, item in value.items():
            check.text(key, where)
            _json_values(check, item, f"{where}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _json_values(check, item, f"{where}[{i}]")
    elif value is not None and not isinstance(value, str | bool):
        check.require(_finite(value), where, "non-finite or non-JSON value")


def _identity(check, identity, where):
    if not isinstance(identity, dict):
        check.errors.append(f"{where}: must be an identity object")
        return
    for key in ("device", "backend", "precision", "library_version"):
        check.nullable(identity, key, where)
    software = identity.get("software")
    check.require(
        isinstance(software, dict) and bool(software),
        where,
        "software must identify measured package versions/revisions",
    )
    if isinstance(software, dict):
        for key in software:
            check.text(software[key], f"{where}.software.{key}")


def _setup(check, item):
    where = f"setup {item['id']!r}"
    for key in ("label", "dataset", "model", "configuration_id"):
        check.text(item.get(key), f"{where}.{key}")
    check.nullable(item, "instrument", where)
    config = item.get("configuration")
    if not isinstance(config, dict):
        check.errors.append(f"{where}: configuration must be an object")
        return
    check.require(bool(config), where, "configuration must describe the setup")
    for key, field in config.items():
        loc = f"{where}.configuration.{key}"
        if not isinstance(field, dict):
            check.errors.append(f"{loc}: must contain value and unit")
            continue
        check.text(field.get("unit"), f"{loc}.unit")
        check.require("value" in field, loc, "missing value")
        if field.get("value") is None:
            check.text(field.get("reason"), f"{loc}.reason")
        # Values can be scalar or vectors (e.g. PSF shape), boolean or strings
        # (e.g. solver). Units may be 'dimensionless' or 'name'.


def _record(check, item, setups):
    where = f"record {item['id']!r}"
    check.reference(item.get("setup_id"), setups, f"{where}.setup_id")
    check.text(item.get("run_id"), f"{where}.run_id")
    metric = item.get("metric")
    check.text(metric, f"{where}.metric")
    axis = item.get("axis")
    check.choice(axis, summary.AXIS_UNITS, f"{where}.axis")
    if isinstance(axis, str) and axis in summary.AXIS_UNITS:
        check.choice(item.get("unit"), summary.AXIS_UNITS[axis], f"{where}.unit")
    meas = item.get("measurement")
    check.require(
        isinstance(meas, dict) and list(meas) == [metric],
        where,
        "measurement must contain exactly its named metric",
    )
    if isinstance(meas, dict):
        for value in meas.values():
            check.require(
                _finite(value) and value >= 0,
                where,
                "measurement must be finite and non-negative; missing cells use selections",
            )
    if axis == "memory":
        check.choice(metric, MEMORY_METRICS, f"{where}.metric")
    _identity(check, item.get("identity"), f"{where}.identity")
    method = item.get("method")
    if not isinstance(method, dict):
        check.errors.append(f"{where}: method must be an object")
    else:
        check.text(method.get("id"), f"{where}.method.id")
        check.nullable(method, "statistic", f"{where}.method")
        check.nullable(method, "repetitions", f"{where}.method", lambda n: _integer(n) and n > 0)
        for key in ("warmup", "synchronization", "cache_state"):
            check.nullable(method, key, f"{where}.method")
    prov = item.get("provenance")
    if not isinstance(prov, dict):
        check.errors.append(f"{where}: provenance must be an object")
    else:
        check.nullable(prov, "host", f"{where}.provenance")
        check.nullable(
            prov, "measured_at", f"{where}.provenance", lambda x: summary.parse_utc(x) is not None
        )
        for key in ("qualified", "has_provenance"):
            check.require(
                isinstance(prov.get(key), bool), where, f"provenance.{key} must be a boolean"
            )
        if prov.get("qualified") is True:
            check.require(
                prov.get("has_provenance") is True, where, "qualified requires provenance"
            )
    status = check.validation(item.get("validation"), f"{where}.validation")
    if status == "accepted":
        check.require(
            isinstance(prov, dict) and prov.get("qualified") is True,
            where,
            "accepted evidence must be qualified",
        )
    check.evidence(item.get("evidence"), f"{where}.evidence")


def _selection(check, item, setups, records):
    where = f"selection {item['id']!r}"
    check.reference(item.get("setup_id"), setups, f"{where}.setup_id")
    check.choice(item.get("status"), SELECTION_STATES, f"{where}.status")
    check.text(item.get("reason"), f"{where}.reason")
    axis = item.get("axis")
    check.choice(axis, summary.AXIS_UNITS, f"{where}.axis")
    if isinstance(axis, str) and axis in summary.AXIS_UNITS:
        check.choice(item.get("unit"), summary.AXIS_UNITS[axis], f"{where}.unit")
    for key in ("metric", "method_id"):
        check.text(item.get(key), f"{where}.{key}")
    _identity(check, item.get("identity"), f"{where}.identity")
    check.nullable(item, "host", where)
    check.require("record_id" in item, where, "missing record_id")
    if item.get("status") not in ("accepted", "unreviewed"):
        check.require(
            item.get("record_id") is None,
            where,
            "unmeasured/failed/unusable/inapplicable cells cannot select a measurement",
        )
        return
    record = check.reference(item.get("record_id"), records, f"{where}.record_id")
    if record is None:
        return
    for key in ("setup_id", "axis", "metric", "unit", "identity"):
        check.require(
            item.get(key) == record.get(key), where, f"{key} mismatch with selected record"
        )
    method = record.get("method")
    check.require(
        isinstance(method, dict) and item.get("method_id") == method.get("id"),
        where,
        "method mismatch with selected record",
    )
    prov = record.get("provenance")
    check.require(
        isinstance(prov, dict) and item.get("host") == prov.get("host"),
        where,
        "host mismatch with selected record",
    )
    validation = record.get("validation")
    check.require(
        isinstance(validation, dict) and validation.get("status") == item.get("status"),
        where,
        "validation status mismatch with selected record",
    )


def _advice(check, item, setups, records, kind):
    where = f"{kind} {item['id']!r}"
    for key in ("title", "description"):
        check.text(item.get(key), f"{where}.{key}")
    scope = item.get("applies_to")
    if not isinstance(scope, dict):
        check.errors.append(f"{where}: applies_to must be an object")
        return
    setup_rows = check.references(scope.get("setup_ids"), setups, f"{where}.applies_to.setup_ids")
    versions = scope.get("library_versions")
    check.require(
        isinstance(versions, list) and bool(versions) and all(summary._text(x) for x in versions),
        where,
        "applicability must name measured library_versions",
    )
    check.text(scope.get("limitations"), f"{where}.applies_to.limitations")
    constraints = scope.get("constraints")
    check.require(
        isinstance(constraints, dict),
        where,
        "applicability constraints must be an object (exact setups apply even when empty)",
    )
    evidence = check.objects(item.get("evidence"), f"{where}.evidence")
    check.require(bool(evidence), where, "needs supporting evidence")
    for ev in evidence:
        check.evidence(ev, f"{where}.evidence")
    if kind == "hazard":
        check.choice(item.get("status"), {"open", "resolved", "unknown"}, f"{where}.status")
    else:
        status = check.validation(item.get("validation"), f"{where}.validation")
        supports = check.references(item.get("record_ids"), records, f"{where}.record_ids")
        allowed_setups = {s["id"] for s in setup_rows}
        for record in supports:
            check.require(
                isinstance(record.get("setup_id"), str)
                and record.get("setup_id") in allowed_setups,
                where,
                "supporting record is outside applicable setups",
            )
            ident = record.get("identity")
            check.require(
                isinstance(ident, dict)
                and isinstance(versions, list)
                and ident.get("library_version") in versions,
                where,
                "supporting record is outside applicable library versions",
            )
            if status == "accepted":
                validation = record.get("validation")
                check.require(
                    isinstance(validation, dict) and validation.get("status") == "accepted",
                    where,
                    "accepted recommendation requires accepted supporting records",
                )


def validate(doc):
    """Return all detected v2 contract violations; never choose a baseline."""
    check = _Check()
    _json_values(check, doc, "summary")
    # The common envelope retains v1 transport/receipt/board fields. Validate
    # it through the established reader with empty records/comparisons; v2
    # records are checked below and v2 deliberately carries no trend pairs.
    envelope = dict(doc, records=[], comparisons=[])
    check.errors.extend(summary._validate_v1(envelope))
    check.require(
        doc.get("comparisons") == [],
        "comparisons",
        "v2 setup feed has no temporal comparisons; must be []",
    )
    setups = check.index(doc.get("setups"), "setups")
    records = check.index(doc.get("records"), "records")
    selections = check.index(doc.get("selections"), "selections")
    for item in setups.values():
        _setup(check, item)
    methods = {}
    for item in records.values():
        _record(check, item, setups)
        method = item.get("method")
        if isinstance(method, dict) and summary._text(method.get("id")):
            prior = methods.setdefault(method["id"], method)
            check.require(prior == method, "records", "method id has conflicting definitions")
    slots = set()
    for item in selections.values():
        _selection(check, item, setups, records)
        # JSON identity includes package revisions; canonical ordering avoids
        # permitting two competing selections just because keys were reordered.
        slot = json.dumps(
            {
                k: item.get(k)
                for k in ("setup_id", "axis", "metric", "unit", "method_id", "identity", "host")
            },
            sort_keys=True,
        )
        check.require(slot not in slots, "selections", "duplicate measurement slot")
        slots.add(slot)
    for field, kind in (("hazards", "hazard"), ("recommendations", "recommendation")):
        for item in check.index(doc.get(field), field).values():
            _advice(check, item, setups, records, kind)
    cov = doc.get("coverage")
    if isinstance(cov, dict):
        expected = cov.get("expected")
        observed = cov.get("observed")
        check.require(
            isinstance(expected, dict)
            and expected.get("cells") == len(selections)
            and type(expected.get("cells")) is int,
            "coverage.expected.cells",
            "must equal the declared selection count",
        )
        if isinstance(observed, dict):
            for key, count in (
                ("setups", len(setups)),
                ("records", len(records)),
                ("selected", sum(s.get("record_id") is not None for s in selections.values())),
            ):
                check.require(
                    observed.get(key) == count and type(observed.get(key)) is int,
                    f"coverage.observed.{key}",
                    "must match catalogue contents",
                )
    return check.errors
