"""Validate the setup-oriented v2 and lifecycle v3 contracts without judging evidence.

Stable setup IDs decouple scientific navigation from script paths. In v2,
selections name exact records and their measurement context; missing cells
remain explicit. In v3 every record declares its own likelihood, setup tuple,
host class, ``class`` (optimal/secondary/experimental) and ``status``
(current/superseded); the producer declares exactly one ``current`` record per
key and Pulse only checks that the declaration is consistent. This module is
stdlib-only and does not read files, choose results, infer an optimal setup or
compute comparisons. See REFERENCE.md for the producer-facing grammar.
"""

from __future__ import annotations

import json
import math
import re

from pulse import summary

SELECTION_STATES = {"accepted", "unreviewed", "not_measured", "failed", "unusable", "inapplicable"}
VALIDATION_STATES = {"accepted", "unreviewed", "rejected"}
MEMORY_METRICS = {"host_peak_rss", "device_peak_allocated", "device_peak_reserved", "device_total"}

# ---- profiling-summary@3 vocabulary (REFERENCE.md, "profiling-summary v3") ----
DATASET_TYPES = {
    "imaging",
    "interferometer",
    "datacube",
    "point_source_image",
    "point_source_source",
    "multi_galaxy",
    "group",
    "cluster",
    "multi_dataset",
    "weak",
}
HOST_CLASSES = set(summary.HOST_CLASSES)
LOCAL_HOST_CLASSES = set(summary.LOCAL_HOST_CLASSES)
_SECONDS = {"s"}
_MEMORY = summary.AXIS_UNITS["memory"]
MEASUREMENT_UNITS = {
    "runtime": _SECONDS,
    "breakdown": _SECONDS,
    "gradient": _SECONDS,
    "compile": _SECONDS,
    "memory_host": _MEMORY,
    "memory_device": _MEMORY,
    "parity": {"dimensionless"},
    "walltime_validation": _SECONDS,
}
CLASSES = {"optimal", "secondary", "experimental"}
STATUSES = {"current", "superseded", "archived"}
SETUP_CHOICES = {
    "backend": {"numba", "jax"},
    "device": {"cpu", "gpu"},
    "operator": {"dense", "sparse", "na"},
    "precision": {"fp64", "mixed"},
    "transformer": {"dft", "nufft", "wtilde", "streaming", "na"},
}
KEY_FIELDS = ("likelihood", "instrument", "setup_id", "host_class", "model_variant", "measurement")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def setup_id(setup: dict) -> str:
    """The canonical ``<backend>_<device>_<operator>_<precision>[_<transformer>]``."""
    parts = [str(setup.get(k)) for k in ("backend", "device", "operator", "precision")]
    if setup.get("transformer") != "na":
        parts.append(str(setup.get("transformer")))
    return "_".join(parts)


def lifecycle_key(item: dict) -> str:
    """The one-``current``-per-key identity of a v3 record or planned cell."""
    return json.dumps({k: item.get(k) for k in KEY_FIELDS}, sort_keys=True)


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


def _list(value):
    return value if isinstance(value, list) else []


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
    _record_body(check, item, where)


def _record_body(check, item, where):
    """Identity, method, provenance, validation and evidence: shared by v2 and v3."""
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


def _likelihood(check, value, where):
    if not isinstance(value, dict):
        check.errors.append(f"{where}: must be a likelihood object {{dataset_type, variant}}")
        return
    check.choice(value.get("dataset_type"), DATASET_TYPES, f"{where}.dataset_type")
    check.text(value.get("variant"), f"{where}.variant")


def _setup_tuple(check, item, where):
    """The compute tuple and its canonical ``setup_id`` (R1 grammar)."""
    setup = item.get("setup")
    if not isinstance(setup, dict):
        check.errors.append(f"{where}.setup: must be an object")
        check.text(item.get("setup_id"), f"{where}.setup_id")
        return
    for key, choices in SETUP_CHOICES.items():
        check.choice(setup.get(key), choices, f"{where}.setup.{key}")
    threads = setup.get("threads")
    check.require(
        threads is None or (_integer(threads) and threads > 0),
        f"{where}.setup.threads",
        "must be a positive integer or null",
    )
    if all(isinstance(setup.get(k), str) and setup.get(k) in c for k, c in SETUP_CHOICES.items()):
        expected = setup_id(setup)
        check.require(
            item.get("setup_id") == expected,
            f"{where}.setup_id",
            f"must be {expected!r} (<backend>_<device>_<operator>_<precision>[_<transformer>])",
        )


def _cell_key_fields(check, item, where):
    """The key fields shared by v3 records and planned cells."""
    _likelihood(check, item.get("likelihood"), f"{where}.likelihood")
    check.text(item.get("instrument"), f"{where}.instrument")
    check.text(item.get("setup_id"), f"{where}.setup_id")
    check.choice(item.get("host_class"), HOST_CLASSES, f"{where}.host_class")
    check.text(item.get("model_variant"), f"{where}.model_variant")
    check.choice(item.get("measurement"), MEASUREMENT_UNITS, f"{where}.measurement")
    check.choice(item.get("class"), CLASSES, f"{where}.class")


def _nullable_text(check, item, key, where):
    check.require(key in item, where, f"missing {key} (null when not applicable)")
    value = item.get(key)
    check.require(value is None or summary._text(value), f"{where}.{key}", "string or null")


# ---- likelihood-lifecycle phase 2x: resources and projected node throughput ----
# Optional on profiling-summary@3 records (additive; REFERENCE.md "Resources and
# projected node throughput"). The producer declares them; Pulse checks their shape
# and internal consistency only. It never recomputes a projection.
NODE_LIMITS = {"cores", "memory", "gpus"}
PROJECTION_STATUSES = {"projected", "not_projected"}


def _positive(value):
    return _finite(value) and value > 0


def _positive_integer(value):
    return _integer(value) and value > 0


def _optional_text(check, block, key, where):
    if key in block:
        value = block[key]
        check.require(value is None or summary._text(value), f"{where}.{key}", "string or null")


def _per_eval(check, block, where):
    """``cpus_per_eval``/``devices_per_eval``/``peak_rss_gb``: shared by both blocks."""
    check.require("cpus_per_eval" in block, where, "missing cpus_per_eval (null when unknown)")
    check.require(
        block.get("cpus_per_eval") is None or _positive_integer(block["cpus_per_eval"]),
        f"{where}.cpus_per_eval",
        "must be a positive integer or null",
    )
    if "devices_per_eval" in block:
        check.require(
            block["devices_per_eval"] is None or _integer(block["devices_per_eval"]),
            f"{where}.devices_per_eval",
            "must be a non-negative integer or null",
        )
    check.require("peak_rss_gb" in block, where, "missing peak_rss_gb (null when unknown)")
    check.require(
        block.get("peak_rss_gb") is None or _positive(block["peak_rss_gb"]),
        f"{where}.peak_rss_gb",
        "must be a finite positive number (GB) or null",
    )
    _optional_text(check, block, "peak_rss_basis", where)


def _resources(check, block, where):
    """What one evaluation occupies, as the producer declared it."""
    if not isinstance(block, dict):
        check.errors.append(f"{where}: must be an object (omit the field when not declared)")
        return
    _per_eval(check, block, where)
    check.require("source" in block, where, "missing source (null when no source exists)")
    for key in ("source", "cpus_per_eval_basis", "peak_rss_note", "sacct_job"):
        _optional_text(check, block, key, where)
    for key in ("reason", "peak_rss_reason"):
        if key in block:
            check.text(block[key], f"{where}.{key}")
    if block.get("cpus_per_eval") is None:
        check.require(
            summary._text(block.get("reason")), where, "cpus_per_eval is null without a reason"
        )
    if block.get("peak_rss_gb") is None:
        check.require(
            summary._text(block.get("reason")) or summary._text(block.get("peak_rss_reason")),
            where,
            "peak_rss_gb is null without a reason or peak_rss_reason",
        )
    _json_values(check, block, where)


def _node_host(check, host, item, where):
    check.text(host.get("host"), f"{where}.host")
    check.require(
        host.get("host_class") == item.get("host_class"),
        f"{where}.host_class",
        f"must be the record's own host_class {item.get('host_class')!r}: a per-call time is "
        "never projected onto another machine",
    )
    limits = host.get("limits")
    device = (
        (item.get("setup") or {}).get("device") if isinstance(item.get("setup"), dict) else None
    )
    if not isinstance(limits, dict) or not limits:
        check.errors.append(f"{where}.limits: must be a non-empty object of worker caps")
        limits = {}
    for key, value in limits.items():
        check.choice(key, NODE_LIMITS, f"{where}.limits key")
        check.require(
            _positive_integer(value), f"{where}.limits.{key}", "must be a positive integer"
        )
    check.require(
        ("gpus" in limits) == (device == "gpu"),
        f"{where}.limits",
        "a gpus limit belongs to a gpu setup only (and a gpu setup declares one)",
    )
    bound_by = host.get("bound_by")
    check.choice(bound_by, NODE_LIMITS, f"{where}.bound_by")
    workers = host.get("workers")
    check.require(_positive_integer(workers), f"{where}.workers", "must be a positive integer")
    if isinstance(bound_by, str) and limits and all(_positive_integer(v) for v in limits.values()):
        check.require(
            bound_by in limits and limits[bound_by] == workers and workers == min(limits.values()),
            f"{where}.bound_by",
            f"must name the smallest limit and equal workers (limits {limits}, workers "
            f"{workers!r}, bound_by {bound_by!r})",
        )
    check.require(
        _positive(host.get("calls_per_s")), f"{where}.calls_per_s", "must be finite and positive"
    )


def _node_throughput(check, block, item, where):
    """``projected_node_throughput``: a projection the producer declares, never a measurement."""
    if not isinstance(block, dict):
        check.errors.append(f"{where}: must be an object (omit the field when not declared)")
        return
    check.require(
        item.get("measurement") == "runtime",
        where,
        "only runtime records carry a node-throughput projection",
    )
    check.require(
        block.get("basis") == "projected",
        f"{where}.basis",
        "must be 'projected' (a projection is never presented as a measurement)",
    )
    status = block.get("status")
    check.choice(status, PROJECTION_STATUSES, f"{where}.status")
    _per_eval(check, block, where)
    per_call = block.get("per_call_s")
    check.require(
        per_call is None or _positive(per_call),
        f"{where}.per_call_s",
        "must be a finite positive number of seconds or null",
    )
    check.text(block.get("per_call_source"), f"{where}.per_call_source")
    eta = block.get("parallel_efficiency")
    if isinstance(eta, dict):
        value = eta.get("value")
        check.require(
            _positive(value) and value <= 1,
            f"{where}.parallel_efficiency.value",
            "must be a number in (0, 1]",
        )
        check.text(eta.get("source"), f"{where}.parallel_efficiency.source")
        _optional_text(check, eta, "kind", f"{where}.parallel_efficiency")
    else:
        check.errors.append(
            f"{where}.parallel_efficiency: must be an object {{value, source[, kind]}}"
        )
    modelled = block.get("not_modelled")
    check.require(
        summary._text(modelled)
        or (
            isinstance(modelled, list)
            and bool(modelled)
            and all(summary._text(m) for m in modelled)
        ),
        f"{where}.not_modelled",
        "must be a non-empty string or list of strings",
    )
    hosts = check.objects(block.get("hosts"), f"{where}.hosts")
    if status == "projected":
        check.require(
            len(hosts) == 1 and len(block.get("hosts") or []) == 1,
            f"{where}.hosts",
            "a projected record names exactly one host (the class it was measured on)",
        )
        check.require(
            per_call is not None, f"{where}.per_call_s", "a projected record needs per_call_s"
        )
        for i, host in enumerate(hosts):
            _node_host(check, host, item, f"{where}.hosts[{i}]")
    elif status == "not_projected":
        check.require(
            block.get("hosts") == [], f"{where}.hosts", "a not_projected record names no host"
        )
        check.text(block.get("reason"), f"{where}.reason")
    _json_values(check, block, where)


def _record_v3(check, item, ids):
    where = f"record {item['id']!r}"
    _cell_key_fields(check, item, where)
    _setup_tuple(check, item, where)
    check.text(item.get("regime"), f"{where}.regime")
    check.text(item.get("run_id"), f"{where}.run_id")
    metric = item.get("metric")
    check.text(metric, f"{where}.metric")
    measurement = item.get("measurement")
    if isinstance(measurement, str) and measurement in MEASUREMENT_UNITS:
        check.choice(item.get("unit"), MEASUREMENT_UNITS[measurement], f"{where}.unit")
    values = item.get("values")
    check.require(
        isinstance(values, dict) and isinstance(metric, str) and metric in values,
        where,
        "values must be a non-empty object containing its headline metric",
    )
    if isinstance(values, dict):
        for value in values.values():
            check.require(
                _finite(value) and value >= 0,
                where,
                "values must be finite and non-negative; missing cells use planned_cells",
            )
    status = item.get("status")
    check.choice(status, STATUSES, f"{where}.status")
    check.require(
        status != "archived",
        where,
        "archived records are not rendered; drop them from records[] and count them in "
        "archive_record_count",
    )
    if status == "current":
        check.require(
            item.get("host_class") not in summary.LOCAL_HOST_CLASSES,
            where,
            f"host_class {item.get('host_class')!r} is never current (laptop and local-GPU rows "
            "are provenance only)",
        )
    check.require("superseded_by" in item, where, "missing superseded_by (null unless superseded)")
    target = item.get("superseded_by")
    if status == "superseded":
        check.require(
            isinstance(target, str) and target in ids and target != item["id"],
            f"{where}.superseded_by",
            f"must name another record in this document, got {target!r}",
        )
    else:
        check.require(target is None, f"{where}.superseded_by", "only superseded records set it")
    _nullable_text(check, item, "decision_id", where)
    if item.get("class") == "optimal":
        check.require(
            summary._text(item.get("decision_id")),
            where,
            "class optimal requires a decision_id (a Pulse designation decision)",
        )
    _nullable_text(check, item, "day_zero", where)
    _nullable_text(check, item, "release_pin", where)
    check.require(
        summary.parse_utc(item.get("measured_at")) is not None,
        f"{where}.measured_at",
        "must be an ISO-8601 UTC timestamp",
    )
    for i, fig in enumerate(check.objects(item.get("figures"), f"{where}.figures")):
        loc = f"{where}.figures[{i}]"
        check.text(fig.get("kind"), f"{loc}.kind")
        check.require(summary.safe_relative_path(fig.get("path")), loc, "unsafe figure path")
        sha = fig.get("sha256")
        check.require(
            isinstance(sha, str) and bool(_SHA256.match(sha)), loc, "sha256 is not 64-hex"
        )
    if "resources" in item:
        _resources(check, item["resources"], f"{where}.resources")
    if "projected_node_throughput" in item:
        _node_throughput(
            check, item["projected_node_throughput"], item, f"{where}.projected_node_throughput"
        )
    _record_body(check, item, where)


def _validate_v3(check, doc):
    """The lifecycle rules: one current per key, optimal ⇒ decision, no archived rows."""
    records = check.index(doc.get("records"), "records")
    ids = set(records)
    for item in records.values():
        _record_v3(check, item, ids)
    current = {}
    for item in records.values():
        if item.get("status") == "current":
            key = lifecycle_key(item)
            prior = current.setdefault(key, item["id"])
            check.require(
                prior == item["id"],
                "records",
                f"second current record {item['id']!r} on the key of {prior!r}; the producer "
                "declares exactly one current per (likelihood, instrument, setup_id, host_class, "
                "model_variant, measurement)",
            )
    planned = check.objects(doc.get("planned_cells", []), "planned_cells")
    seen = set()
    for i, cell in enumerate(planned):
        where = f"planned_cells[{i}]"
        _cell_key_fields(check, cell, where)
        key = lifecycle_key(cell)
        check.require(key not in seen, where, "duplicate planned cell")
        seen.add(key)
    count = doc.get("archive_record_count")
    check.require(
        _integer(count), "archive_record_count", "must be a non-negative integer (0 when none)"
    )
    # Advice keeps the v2 shape; its setup_ids name the canonical v3 setup_ids.
    setups = {
        r["setup_id"]: {"id": r["setup_id"]}
        for r in records.values()
        if summary._text(r.get("setup_id"))
    }
    for field, kind in (("hazards", "hazard"), ("recommendations", "recommendation")):
        for item in check.index(doc.get(field, []), field).values():
            _advice(check, item, setups, records, kind)
    cov = doc.get("coverage")
    if isinstance(cov, dict):
        expected, observed = cov.get("expected"), cov.get("observed")
        check.require(
            isinstance(expected, dict)
            and type(expected.get("cells")) is int
            and expected.get("cells") == len(planned),
            "coverage.expected.cells",
            "must equal the planned_cells count",
        )
        if isinstance(observed, dict):
            counts = lifecycle_counts(doc)
            check.require(
                type(observed.get("records")) is int and observed.get("records") == len(records),
                "coverage.observed.records",
                "must match catalogue contents",
            )
            for key in ("current", "superseded"):
                if key in observed:
                    check.require(
                        observed[key] == counts[key],
                        f"coverage.observed.{key}",
                        "must match catalogue contents",
                    )


def lifecycle_counts(doc: dict) -> dict:
    """``{current, superseded, archived}`` as the producer declared them (v3 only)."""
    records = [r for r in _list(doc.get("records")) if isinstance(r, dict)]
    count = doc.get("archive_record_count")
    return {
        "current": sum(r.get("status") == "current" for r in records),
        "superseded": sum(r.get("status") == "superseded" for r in records),
        "archived": count if _integer(count) else 0,
    }


def decision_ids(doc: dict) -> list[str]:
    """Every ``decision_id`` a v3 document names, for the repo-aware resolution step."""
    return sorted(
        {
            r["decision_id"]
            for r in _list(doc.get("records"))
            if isinstance(r, dict) and summary._text(r.get("decision_id"))
        }
    )


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


def validate(doc, version=2):
    """Return all detected v2/v3 contract violations; never choose a baseline.

    v3 resolves ``decision_id`` presence only; resolving each id against the
    organ's ``decisions.yaml`` is the repo-aware step in ``pulse.ingest``.
    """
    check = _Check()
    _json_values(check, doc, "summary")
    # The common envelope retains v1 transport/receipt/board fields. Validate
    # it through the established reader with empty records/comparisons; v2/v3
    # records are checked below and neither carries trend pairs.
    envelope = dict(doc, records=[], comparisons=[])
    check.errors.extend(summary._validate_v1(envelope))
    check.require(
        doc.get("comparisons") == [],
        "comparisons",
        f"v{version} setup feed has no temporal comparisons; must be []",
    )
    if version == 3:
        _validate_v3(check, doc)
        return check.errors
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
