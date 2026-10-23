"""Flat links to human-authored campaign decisions; never infer conclusions.

An entry may carry ``kind: designation``: the human's choice of the optimal and
secondary setups for one likelihood, regime and hardware class. A
``profiling-summary@3`` record with ``class: optimal`` names such an entry in
its ``decision_id``; Pulse checks that the id resolves and never derives a
designation from timings.
"""

import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from pulse import ORGAN_ROOT, catalogue

REPO = "PyAutoPulse"
BASE_FIELDS = {"id", "title", "date", "url"}
DESIGNATION_FIELDS = {
    "likelihood",
    "regime",
    "hardware_class",
    "optimal",
    "secondary",
    "evidence",
    "rule",
    "supersedes",
}
HARDWARE_CLASSES = {"cpu_many_core", "gpu_a100", "laptop"}
_SETUP_ID = re.compile(
    "^({backend})_({device})_({operator})_({precision})(_({transformer}))?$".format(
        **{
            k: "|".join(sorted(v - {"na"} if k == "transformer" else v))
            for k, v in catalogue.SETUP_CHOICES.items()
        }
    )
)
_LIKELIHOOD = re.compile(
    "^(" + "|".join(sorted(catalogue.DATASET_TYPES)) + r")/[a-z0-9]+(?:_[a-z0-9]+)*$"
)


def _line(value) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(ord(c) < 32 for c in value)


def _designation(row: dict) -> None:
    """Validate the designation fields of one ``kind: designation`` entry."""
    key = row["id"]
    missing = sorted(DESIGNATION_FIELDS - set(row))
    if missing:
        raise ValueError(f"Designation {key} lacks {', '.join(missing)}")
    if not (isinstance(row["likelihood"], str) and _LIKELIHOOD.match(row["likelihood"])):
        raise ValueError(f"Designation {key}: likelihood must be <dataset_type>/<variant>")
    if not _line(row["regime"]) or not _line(row["rule"]):
        raise ValueError(f"Designation {key}: regime and rule must be single-line strings")
    if row["hardware_class"] not in HARDWARE_CLASSES:
        raise ValueError(
            f"Designation {key}: hardware_class must be one of {sorted(HARDWARE_CLASSES)}"
        )
    secondary = row["secondary"]
    if not isinstance(secondary, list):
        raise ValueError(f"Designation {key}: secondary must be a list of setup_ids")
    for setup in [row["optimal"], *secondary]:
        if not (isinstance(setup, str) and _SETUP_ID.match(setup)):
            raise ValueError(f"Designation {key}: {setup!r} is not a canonical setup_id")
    if row["optimal"] in secondary or len(set(secondary)) != len(secondary):
        raise ValueError(f"Designation {key}: optimal and secondary setups must be distinct")
    evidence = row["evidence"]
    if not (isinstance(evidence, list) and evidence and all(_line(e) for e in evidence)):
        raise ValueError(f"Designation {key}: evidence must be a non-empty list of record ids")
    if row["supersedes"] is not None and not _line(row["supersedes"]):
        raise ValueError(f"Designation {key}: supersedes must be a decision id or null")


def load(root: Path = ORGAN_ROOT) -> list[dict]:
    """Validate the index and locally owned records; remote records stay links."""
    try:
        document = yaml.safe_load((root / "decisions.yaml").read_text())
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Decision history: {exc}") from exc
    if (
        not isinstance(document, dict)
        or set(document) != {"decisions"}
        or not isinstance(document["decisions"], list)
    ):
        raise ValueError("Decision history requires a decisions list")
    seen = set()
    rows = []
    for row in document["decisions"]:
        if not isinstance(row, dict):
            raise ValueError("Decision requires id, title, date and url")
        kind = row.get("kind")
        allowed = BASE_FIELDS | ({"kind"} | DESIGNATION_FIELDS if kind == "designation" else set())
        if not BASE_FIELDS <= set(row) or not set(row) <= allowed:
            raise ValueError(
                "Decision requires id, title, date and url"
                + ("" if kind in (None, "designation") else "; kind must be designation")
            )
        if any(
            not isinstance(row[k], str) or not row[k].strip() or any(ord(c) < 32 for c in row[k])
            for k in BASE_FIELDS
        ):
            raise ValueError("Decision fields must be nonempty single-line strings; quote dates")
        key = row["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in seen:
            raise ValueError(f"Invalid or duplicate decision id: {key}")
        seen.add(key)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["date"]):
            raise ValueError("Decision date must be YYYY-MM-DD")
        date.fromisoformat(row["date"])
        url = urlsplit(row["url"])
        match = re.fullmatch(
            r"/PyAutoLabs/(PyAutoPulse|PyAutoInsight)/blob/main/decisions/([a-z0-9-]+)\.md",
            url.path,
        )
        if (
            url.scheme != "https"
            or url.netloc != "github.com"
            or url.query
            or url.fragment
            or not match
            or match[2] != key
        ):
            raise ValueError(
                "Decision URL must link to its canonical GitHub decisions/<id>.md record"
            )
        if match[1] == REPO:
            path = root / "decisions" / f"{key}.md"
            if not path.is_file():
                raise ValueError(f"Missing decision record: {path}")
            content = path.read_text()
            if (
                not content.startswith(f"# {row['title']}\n")
                or f"Date: {row['date']}\n" not in content
            ):
                raise ValueError(f"Decision title/date differ from index: {key}")
        if kind == "designation":
            _designation(row)
        rows.append(dict(row))
    for row in rows:
        if row.get("supersedes") is not None and row["supersedes"] not in seen:
            raise ValueError(f"Designation {row['id']} supersedes unknown {row['supersedes']}")
    return sorted(rows, key=lambda row: (row["date"], row["id"]), reverse=True)


def ids(root: Path = ORGAN_ROOT) -> set[str]:
    """Every decision id in the validated index (``ValueError`` when it is invalid)."""
    return {row["id"] for row in load(root)}


def marker(rows):
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    return f"<!-- decision-history:{digest} -->"


def render_html(rows=None):
    rows = load() if rows is None else rows
    links = "".join(
        f'<a class="model-choice" href="{html.escape(row["url"], quote=True)}" target="_blank" rel="noopener" title="Opens in a new tab">'
        f"{html.escape(row['title'])}</a>"
        for row in rows
    )
    return (
        marker(rows)
        + '<section id="decision-history"><h2>Decision History</h2>'
        + (links or "<p>No decisions recorded yet.</p>")
        + "</section>"
    )


def markdown(rows=None):
    rows = load() if rows is None else rows
    # HTML anchors also work in GitHub Markdown and safely escape arbitrary titles.
    links = [
        f'- <a href="{html.escape(row["url"], quote=True)}">{html.escape(row["title"])}</a>'
        for row in rows
    ]
    return "\n".join(
        [marker(rows), "## Decision History", "", *(links or ["No decisions recorded yet."]), ""]
    )
