"""Validate the ``walltime-validation`` v1 evidence axis without judging it.

A wall-time validation record is a **full-fit** measurement: one sampler run of
one likelihood, setup and seed, with its wall time, likelihood evaluations and
the producer's own comparison against the per-likelihood ``runtime`` record it
names. Every derived number (``implied_ms_per_eval``, ``predicted_ms_per_eval``,
``ratio_measured_over_predicted``, ``parallel_efficiency``) is computed and
declared by the producer; Pulse validates the shape and renders the values. It
computes no ratio, infers no optimal setup and never reads a full-fit time as a
per-likelihood measurement (or the reverse). Stdlib only. See REFERENCE.md.

The producer's join to a profiling runtime record (``profiling_record_id``,
``profiling_per_call_s``, ``size_match`` and friends) and ``implied_s_per_eval``
are additive optional fields: absent is valid; present, they are type-checked.
"""

from __future__ import annotations

import json
import re

from pulse import catalogue, summary

ENVELOPE = ("schema", "version", "project", "generated_at", "producer_revision", "records")
PARITY_STATUSES = {"match", "diverged", "not_assessed"}
NUMERIC = (
    "wall_s",
    "implied_ms_per_eval",
    "predicted_ms_per_eval",
    "ratio_measured_over_predicted",
    "parallel_efficiency",
    "max_log_likelihood",
)
# Additive optional fields (still walltime-validation@1): checked only when present.
OPTIONAL_NUMERIC = ("implied_s_per_eval", "profiling_per_call_s")
OPTIONAL_TEXT = (
    "profiling_record_id",
    "profiling_unmatched_reason",
    "profiling_per_call_source",
    "profiling_status",
)
OPTIONAL_COUNT = ("source_pixels", "profiling_source_pixels")
KEY_FIELDS = (
    "likelihood",
    "instrument",
    "setup_id",
    "host_class",
    "model_variant",
    "sampler",
    "seed",
)
_SHA = re.compile(r"^[0-9a-f]{40}$")


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def key(record: dict) -> str:
    """The identity of one full-fit run: one record per key."""
    return json.dumps({k: record.get(k) for k in KEY_FIELDS}, sort_keys=True)


def _record(check, item, where):
    catalogue._likelihood(check, item.get("likelihood"), f"{where}.likelihood")
    check.text(item.get("instrument"), f"{where}.instrument")
    check.text(item.get("setup_id"), f"{where}.setup_id")
    check.choice(item.get("host_class"), catalogue.HOST_CLASSES, f"{where}.host_class")
    check.text(item.get("model_variant"), f"{where}.model_variant")
    check.text(item.get("sampler"), f"{where}.sampler")
    check.require(_count(item.get("seed")), f"{where}.seed", "must be a non-negative integer")
    for field in NUMERIC:
        check.require(field in item, where, f"missing {field} (null when not measured)")
        check.require(
            summary._finite_or_null(item.get(field)), f"{where}.{field}", "finite number or null"
        )
    for field in ("likelihood_evals", "cores"):
        value = item.get(field)
        check.require(field in item, where, f"missing {field} (null when not recorded)")
        check.require(
            value is None or _count(value), f"{where}.{field}", "non-negative integer or null"
        )
    for field in ("reference_runtime_record_id", "release_pin", "slurm_job_id"):
        check.require(field in item, where, f"missing {field} (null when not applicable)")
        value = item.get(field)
        check.require(value is None or summary._text(value), f"{where}.{field}", "string or null")
    check.choice(item.get("parity_status"), PARITY_STATUSES, f"{where}.parity_status")
    for field in OPTIONAL_NUMERIC:
        if field in item:
            check.require(
                summary._finite_or_null(item[field]), f"{where}.{field}", "finite number or null"
            )
    for field in OPTIONAL_TEXT:
        if field in item:
            value = item[field]
            check.require(
                value is None or summary._text(value), f"{where}.{field}", "string or null"
            )
    for field in OPTIONAL_COUNT:
        if field in item:
            value = item[field]
            check.require(
                value is None or _count(value), f"{where}.{field}", "non-negative integer or null"
            )
    if "size_match" in item:
        value = item["size_match"]
        check.require(
            value is None or isinstance(value, bool), f"{where}.size_match", "boolean or null"
        )


def validate(doc) -> list[str]:
    """Every contract break in a ``walltime-validation@1`` document (empty = valid)."""
    if not isinstance(doc, dict):
        return ["summary is not a JSON object"]
    check = catalogue._Check()
    catalogue._json_values(check, doc, "summary")
    check.errors += [f"missing required field {k!r}" for k in ENVELOPE if k not in doc]
    check.require(summary._text(doc.get("project")), "project", "must be a non-empty string")
    check.require(
        summary.parse_utc(doc.get("generated_at")) is not None,
        "generated_at",
        "must be an ISO-8601 UTC timestamp",
    )
    rev = doc.get("producer_revision")
    check.require(
        rev is None or (isinstance(rev, str) and bool(_SHA.match(rev))),
        "producer_revision",
        f"is not a 40-hex commit or null: {rev!r}",
    )
    lim = doc.get("limitations", [])
    check.require(
        isinstance(lim, list) and all(summary._text(x) for x in lim),
        "limitations",
        "must be a list of non-empty strings",
    )
    records = check.index(doc.get("records"), "records")
    seen: dict[str, str] = {}
    for rid, item in records.items():
        where = f"record {rid!r}"
        _record(check, item, where)
        prior = seen.setdefault(key(item), rid)
        check.require(prior == rid, where, f"duplicate key of record {prior!r}")
    return check.errors
