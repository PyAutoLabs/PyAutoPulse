"""Render setup navigation from captured v2/v3 evidence; never select scientific truth.

A v3 (lifecycle) catalogue renders a Class-first browser: Class (Optimal by
default) → Likelihood (dataset type → variant) → Instrument → Hardware class →
Measurement, showing ``status: current`` rows unless History is ticked. The
producer declares class and status; the board ranks nothing, picks no fastest
row and shows archived records only as a count.
"""

from __future__ import annotations

import html
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import quote

from pulse import ORGAN_ROOT, catalogue


def theme():
    candidates = [Path(os.environ["PYAUTO_BRAIN"])] if os.environ.get("PYAUTO_BRAIN") else []
    candidates += [ORGAN_ROOT.parent / "PyAutoBrain", ORGAN_ROOT / "_brain"]
    for root in candidates:
        path = root / "board/_theme.py"
        if path.is_file():
            spec = importlib.util.spec_from_file_location("pulse_board_theme", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("Shared theme unavailable: set PYAUTO_BRAIN to a PyAutoBrain checkout.")


def assets():
    return (
        (ORGAN_ROOT / "pulse/setup_browser.css").read_text(),
        (ORGAN_ROOT / "pulse/measurement_presentation.js").read_text()
        + "\n"
        + (ORGAN_ROOT / "pulse/setup_browser.js").read_text(),
    )


CLASS_OPTIONS = (
    ("optimal", "Optimal"),
    ("secondary", "Secondary"),
    ("experimental", "Experimental"),
    ("all", "All"),
)
# The selector order after Class; each is a data-* attribute on every row.
FILTERS = (
    ("dataset_type", "Likelihood"),
    ("variant", "Variant"),
    ("instrument", "Instrument"),
    ("host_class", "Hardware class"),
    ("measurement", "Measurement"),
)


def lifecycle(doc) -> bool:
    return isinstance(doc, dict) and doc.get("version") == 3


def _row_fields(record):
    likelihood = record.get("likelihood") or {}
    return {
        "class": record.get("class"),
        "status": record.get("status"),
        "dataset_type": likelihood.get("dataset_type"),
        "variant": likelihood.get("variant"),
        "instrument": record.get("instrument"),
        "host_class": record.get("host_class"),
        "measurement": record.get("measurement"),
    }


def default_visible(record) -> bool:
    """The default view: Optimal class, current status, no other filter."""
    return record.get("class") == "optimal" and record.get("status") == "current"


def not_measured(doc) -> list[dict]:
    """Optimal planned cells with no current record on their key (producer-declared)."""
    current = {
        catalogue.lifecycle_key(r) for r in doc.get("records") or [] if r.get("status") == "current"
    }
    return [
        cell
        for cell in doc.get("planned_cells") or []
        if cell.get("class") == "optimal" and catalogue.lifecycle_key(cell) not in current
    ]


def _cell_label(cell):
    likelihood = cell.get("likelihood") or {}
    return (
        f"{likelihood.get('dataset_type')}/{likelihood.get('variant')} · {cell.get('instrument')} · "
        f"{cell.get('setup_id')} · {cell.get('host_class')} · {cell.get('model_variant')} · "
        f"{cell.get('measurement')}"
    )


def _value(record):
    values = record.get("values") or {}
    metric = record.get("metric")
    return f"{values.get(metric)} {record.get('unit')} ({metric})"


# Per-call (measured, the default) ↔ per-node (the producer's projection). The
# default stays per-call until phase 4 measures η, so a projection never headlines.
VIEW_OPTIONS = (
    ("per_call", "Per call (measured)"),
    ("per_node", "Per node (projected)"),
)
PNT = "projected_node_throughput"


def _number(value):
    return f"{value:g}" if isinstance(value, int | float) and not isinstance(value, bool) else "?"


def node_throughput(record):
    """``(kind, text, detail)`` for the producer's declared projection, never computed here.

    ``kind`` is ``projected``, ``not_projected`` or ``None`` (no block declared).
    ``detail`` is the tooltip text: η, its source, the bounding limit, the per-call
    basis and what is not modelled.
    """
    block = record.get(PNT)
    if not isinstance(block, dict):
        return None, "no node projection declared", ""
    if block.get("status") != "projected" or not block.get("hosts"):
        return "not_projected", f"not projected: {block.get('reason') or 'no reason given'}", ""
    host = block["hosts"][0]
    eta = block.get("parallel_efficiency") or {}
    limits = ", ".join(f"{k} {_number(v)}" for k, v in (host.get("limits") or {}).items())
    modelled = block.get("not_modelled")
    if isinstance(modelled, list):
        modelled = "; ".join(str(m) for m in modelled)
    text = (
        f"{_number(host.get('calls_per_s'))} calls/s · {_number(host.get('workers'))} workers "
        f"({host.get('bound_by')}-bound) on {host.get('host')}"
    )
    detail = (
        f"Projected, not measured. η (parallel efficiency) {_number(eta.get('value'))}"
        + (f" ({eta['kind']})" if eta.get("kind") else "")
        + f", source: {eta.get('source')}. Bound by {host.get('bound_by')} "
        f"(worker caps: {limits}). Per call {_number(block.get('per_call_s'))} s from "
        f"{block.get('per_call_source')}. Not modelled: {modelled}"
    )
    return "projected", text, detail


def _node_cell(record, tip_id, e):
    kind, text, detail = node_throughput(record)
    if kind == "projected":
        return (
            f"{e(text)} <span class='projected-wrap'><span class='projected-badge' tabindex='0' "
            f"aria-describedby='{e(tip_id)}'>projected</span><span class='projected-tip' "
            f"role='tooltip' id='{e(tip_id)}'>{e(detail)}</span></span>"
        )
    return f"<span class='muted'>{e(text)}</span>" if kind else "<span class='muted'>—</span>"


def _render_lifecycle(snapshot):
    doc = snapshot.doc
    instance = snapshot.instance
    e = lambda v: html.escape(str(v), quote=True)  # noqa: E731
    records = [r for r in doc.get("records") or [] if isinstance(r, dict)]
    counts = catalogue.lifecycle_counts(doc)
    fields = [
        f'<label for="lifecycle-{e(instance.instance)}-class">Class'
        f'<select id="lifecycle-{e(instance.instance)}-class" data-filter="class">'
        + "".join(
            f'<option value="{v}"{" selected" if v == "optimal" else ""}>{t}</option>'
            for v, t in CLASS_OPTIONS
        )
        + "</select></label>"
    ]
    for key, title in FILTERS:
        values = sorted({str(_row_fields(r)[key]) for r in records})
        fields.append(
            f'<label for="lifecycle-{e(instance.instance)}-{key}">{title}'
            f'<select id="lifecycle-{e(instance.instance)}-{key}" data-filter="{key}">'
            '<option value="" selected>All</option>'
            + "".join(f'<option value="{e(v)}">{e(v)}</option>' for v in values)
            + "</select></label>"
        )
    fields.append(
        '<label class="history-toggle"><input type="checkbox" data-filter="history"> '
        "History (include superseded)</label>"
    )
    fields.append(
        f'<label for="lifecycle-{e(instance.instance)}-view">View'
        f'<select id="lifecycle-{e(instance.instance)}-view" data-view>'
        + "".join(
            f'<option value="{v}"{" selected" if v == "per_call" else ""}>{t}</option>'
            for v, t in VIEW_OPTIONS
        )
        + "</select></label>"
    )
    rows = []
    for n, r in enumerate(records):
        attrs = "".join(f' data-{k.replace("_", "-")}="{e(v)}"' for k, v in _row_fields(r).items())
        hidden = "" if default_visible(r) else " hidden"
        ev = r.get("evidence") or {}
        links = []
        if ev.get("path"):
            url = instance.blob_url(snapshot.commit, quote(ev["path"], safe="/"))
            links.append(f'<a href="{e(url)}">evidence</a>')
        for fig in r.get("figures") or []:
            url = instance.blob_url(snapshot.commit, quote(fig["path"], safe="/"))
            links.append(f'<a href="{e(url)}">{e(fig["kind"])} figure</a>')
        likelihood = r.get("likelihood") or {}
        rows.append(
            f'<tr data-record="{e(r.get("id"))}"{attrs}{hidden}>'
            f"<td>{e(likelihood.get('dataset_type'))}/{e(likelihood.get('variant'))}</td>"
            f"<td>{e(r.get('instrument'))}</td><td>{e(r.get('regime'))}</td>"
            f"<td><code>{e(r.get('setup_id'))}</code></td><td>{e(r.get('host_class'))}</td>"
            f"<td>{e(r.get('model_variant'))}</td><td>{e(r.get('measurement'))}</td>"
            f"<td class='num'><span data-view-value='per_call'>{e(_value(r))}</span>"
            f"<span data-view-value='per_node' hidden>"
            f"{_node_cell(r, f'pnt-{instance.instance}-{n}', e)}</span></td>"
            f"<td>{e(r.get('class'))}</td>"
            f"<td>{e(r.get('status'))}</td><td>{e(r.get('decision_id') or '—')}</td>"
            f"<td>{' · '.join(links) or '—'}</td></tr>"
        )
    visible = sum(default_visible(r) for r in records)
    missing = not_measured(doc)
    coverage = (
        f'<details class="lifecycle-coverage" data-id="coverage"><summary>Coverage: '
        f"{len(missing)} optimal cell{'' if len(missing) == 1 else 's'} not measured</summary>"
        + (
            "<ul>" + "".join(f"<li>{e(_cell_label(c))}</li>" for c in missing) + "</ul>"
            if missing
            else "<p>Every planned optimal cell has a current record.</p>"
        )
        + "</details>"
    )
    label = instance.repo.removesuffix("_profiling").replace("autolens", "PyAutoLens")
    return (
        f'<section class="setup-browser lifecycle-browser" data-setup-browser="{e(instance.instance)}" '
        f'data-lifecycle aria-label="{e(instance.repo)} setups">'
        f"<h3>{e(label)}: setups by class</h3>"
        f'<div class="selectors lifecycle-selectors">{"".join(fields)}</div>'
        f'<p data-id="lifecycle-counts">{counts["current"]} current · {counts["superseded"]} '
        f"superseded (shown with History) · {counts['archived']} archived (counted, not shown). "
        "Class and status are the producer's declarations; this board ranks nothing.</p>"
        '<p class="view-note" data-view-value="per_node" data-id="view-note" hidden>'
        "Per node shows the producer's <b>projected</b> calls per second on the host class "
        "each row was measured on: workers capped by cores ÷ CPUs per evaluation and memory "
        "÷ peak RSS (one per GPU), times a declared parallel efficiency η, over the per-call "
        "time. η is not yet measured, so these are upper bounds; focus a <b>projected</b> "
        "badge for its basis. Never compare GPU and CPU setups on per-call latency alone.</p>"
        '<div class="tablewrap"><table class="lifecycle-table"><thead><tr><th>Likelihood</th>'
        "<th>Instrument</th><th>Regime</th><th>Setup</th><th>Hardware class</th>"
        "<th>Model variant</th><th>Measurement</th><th>"
        "<span data-view-value='per_call'>Value (producer)</span>"
        "<span data-view-value='per_node' hidden>Node throughput (producer projection)</span>"
        "</th><th>Class</th>"
        "<th>Status</th><th>Decision</th><th>Evidence</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        f'<p class="empty" data-id="no-rows"{" hidden" if visible else ""}>'
        "No record matches this selection.</p>" + coverage + "</section>"
    )


def render(snapshot):
    doc = snapshot.doc or {}
    if lifecycle(doc):
        return _render_lifecycle(snapshot)
    if doc.get("version") != 2:
        return ""
    instance = snapshot.instance
    payload = {
        "catalogue": doc,
        "instance": instance.instance,
        "label": instance.repo.removesuffix("_profiling").replace("autolens", "PyAutoLens"),
        "repo": instance.github_url,
        "commit": snapshot.commit,
        "shard_base": f"https://raw.githubusercontent.com/{instance.github}/{snapshot.commit}/{instance.summary_path.rsplit('/', 1)[0]}/",
        "local": snapshot.source == "local",
    }
    # A local checkout's dirty files have no immutable remote representation.
    payload["remote_shards"] = bool(snapshot.commit and snapshot.source == "remote")
    encoded = (
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("&", "\\u0026")
    )
    fallback = []
    for setup in doc.get("setups", []):
        ev = setup.get("evidence")
        if ev:
            url = instance.blob_url(snapshot.commit, quote(ev["path"], safe="/"))
            fallback.append(
                f'<li><a href="{html.escape(url, quote=True)}">{html.escape(setup["dataset"])} / {html.escape(setup["model"])} / {html.escape(setup.get("instrument") or "unspecified")} — {html.escape(ev["path"])}</a></li>'
            )
    return (
        f'<section class="setup-browser" data-setup-browser="{html.escape(instance.instance)}" aria-label="{html.escape(instance.repo)} setups">'
        '<script type="application/json" class="setup-payload">' + encoded + "</script>"
        '<p data-id="load-status" role="status" aria-live="polite"></p>'
        '<div data-id="navigation"></div><section data-id="results" aria-label="Selected setup" hidden></section>'
        "<noscript><details><summary>Original setup evidence (JavaScript disabled)</summary><ul>"
        + "".join(fallback)
        + "</ul></details></noscript></section>"
    )


def _node_markdown(record):
    kind, text, detail = node_throughput(record)
    if kind == "projected":
        block = record[PNT]
        eta = block.get("parallel_efficiency") or {}
        return f"{text} — *projected*, η {_number(eta.get('value'))} ({eta.get('source')})"
    return text if kind else "—"


def _markdown_lifecycle(snapshot):
    doc = snapshot.doc
    counts = catalogue.lifecycle_counts(doc)
    name = snapshot.instance.repo.removesuffix("_profiling")
    lines = [
        f"<details><summary>{html.escape(name)} — optimal, current setups</summary>",
        "",
        f"[Interactive setup browser]({snapshot.instance.dashboard_url})",
        "",
        f"{counts['current']} current · {counts['superseded']} superseded · "
        f"{counts['archived']} archived (counted, not shown). Class and status are the "
        "producer's declarations.",
        "",
        "| Likelihood | Instrument | Setup | Hardware class | Model variant | Measurement "
        "| Value (producer) | Decision | Node throughput (projected) |",
        "|---|---|---|---|---|---|---:|---|---|",
    ]
    esc = lambda v: html.escape(str(v)).replace("|", "\\|")  # noqa: E731
    for r in doc.get("records") or []:
        if not default_visible(r):
            continue
        likelihood = r.get("likelihood") or {}
        lines.append(
            f"| {esc(likelihood.get('dataset_type'))}/{esc(likelihood.get('variant'))} "
            f"| {esc(r.get('instrument'))} | `{esc(r.get('setup_id'))}` | {esc(r.get('host_class'))} "
            f"| {esc(r.get('model_variant'))} | {esc(r.get('measurement'))} | {esc(_value(r))} "
            f"| {esc(r.get('decision_id'))} | {esc(_node_markdown(r))} |"
        )
    missing = not_measured(doc)
    lines += ["", f"Coverage: {len(missing)} optimal cell(s) not measured.", ""]
    lines += [f"- {esc(_cell_label(c))}" for c in missing]
    lines += ["", "</details>", ""]
    return lines


def markdown(snapshot):
    doc = snapshot.doc or {}
    if lifecycle(doc):
        return _markdown_lifecycle(snapshot)
    lines = [
        f"<details><summary>{snapshot.instance.repo.removesuffix('_profiling')} — choose a setup</summary>",
        "",
        f"[Interactive setup browser]({snapshot.instance.dashboard_url})",
        "",
    ]
    for dataset in sorted({s["dataset"] for s in doc.get("setups", [])}):
        lines += [f"<details><summary>{html.escape(dataset)}</summary>", ""]
        for model in sorted({s["model"] for s in doc["setups"] if s["dataset"] == dataset}):
            lines += [
                f"- **{html.escape(model)}**: "
                + ", ".join(
                    sorted(
                        {
                            html.escape(s.get("instrument") or "unspecified")
                            for s in doc["setups"]
                            if s["dataset"] == dataset and s["model"] == model
                        }
                    )
                )
            ]
        lines += ["", "</details>", ""]
    lines += ["</details>", ""]
    return lines
