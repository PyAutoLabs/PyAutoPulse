"""Render setup navigation from captured v2/v3 evidence; never select scientific truth.

A v3 (lifecycle) catalogue renders a runtime-only table: filters Class (All by
default) → Dataset type → Model → Instrument → Hardware class, one row per
``runtime`` record showing ``status: current`` rows unless History is ticked.
Runtime s is the producer's vmap per-call time and Est. 12-core s its
``estimated_12_core`` value (numba CPU only), both rounded for display; each row
opens a detail page. The producer declares class and status; the board ranks
nothing, picks no fastest row and shows archived records only as a count.
"""

from __future__ import annotations

import html
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode

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
    ("all", "All"),
    ("optimal", "Optimal"),
    ("secondary", "Secondary"),
    ("experimental", "Experimental"),
)
# The selector order after Class; each is a data-* attribute on every row.
FILTERS = (
    ("dataset_type", "Dataset type"),
    ("variant", "Model"),
    ("instrument", "Instrument"),
    ("host_class", "Hardware class"),
)
PRECISIONS = ("fp64", "fp32", "fp16", "bf16", "mixed")
PNT = "projected_node_throughput"
KNOWLEDGE_URL = (
    "https://github.com/PyAutoLabs/PyAutoPulse/blob/main/knowledge/cpu_parallel_vs_gpu_batched.md"
)
KNOWLEDGE_TITLE = "Comparing CPU-parallel and GPU-batched setups"
DP = 5  # display rounding of every per-call time (presentation only)


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
    }


def precision(setup_id) -> str | None:
    """The precision token a setup id carries (``fp64``, ``fp32``, ``mixed``…), if any."""
    return next((t for t in str(setup_id or "").split("_") if t in PRECISIONS), None)


def setup_label(setup_id) -> str:
    """The setup id without its precision token: ``jax_gpu_sparse_fp64`` → ``jax_gpu_sparse``."""
    return "_".join(t for t in str(setup_id or "").split("_") if t not in PRECISIONS)


def variant_label(model_variant, setup_id) -> str:
    """The model variant, with a non-fp64 precision appended (``default+mixed``)."""
    p = precision(setup_id)
    return str(model_variant) if p in (None, "fp64") else f"{model_variant}+{p}"


def runtime_rows(doc) -> list[dict]:
    """The v3 ``runtime`` records the table shows (current, and superseded with History)."""
    return [
        r
        for r in (doc or {}).get("records") or []
        if isinstance(r, dict)
        and r.get("measurement") == "runtime"
        and r.get("status") in ("current", "superseded")
    ]


def default_visible(record) -> bool:
    """The default view: every class, current status, no other filter."""
    return record.get("status") == "current"


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


def _real(value) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def fixed(value, dp: int = DP) -> str | None:
    """``value`` rounded to ``dp`` decimal places for display, else None."""
    return f"{value:.{dp}f}" if _real(value) else None


def runtime_s(record):
    """The producer's vmap per-call time (``projected_node_throughput.per_call_s``)."""
    block = record.get(PNT)
    return block.get("per_call_s") if isinstance(block, dict) else None


def twelve_core_s(record):
    """The producer's ``estimated_12_core.value_s`` (numba CPU records only)."""
    block = record.get("estimated_12_core")
    return block.get("value_s") if isinstance(block, dict) else None


def _number(value):
    return f"{value:g}" if _real(value) else "?"


def node_throughput(record):
    """``(kind, text, detail)`` for the producer's declared projection, never computed here.

    ``kind`` is ``projected``, ``not_projected`` or ``None`` (no block declared).
    ``detail`` is the explanation: η, its source, the bounding limit, the per-call
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


def _e(value) -> str:
    return html.escape(str(value), quote=True)


def time_cell(value, title: str, missing: str) -> str:
    """A bold, right-aligned 5-DP time cell; the exact value stays in the tooltip."""
    shown = fixed(value)
    if shown is None:
        return f"<td class='num'><span class='muted' title='{_e(missing)}'>—</span></td>"
    return f"<td class='num'><b title='{_e(f'{value} s · {title}')}'>{shown}</b></td>"


def detail_href(view: str, instance: str, record_id: str) -> str:
    """The same-page route of one detail page (``?view=setup|run&instance=&record=``)."""
    return "?" + urlencode({"view": view, "instance": instance, "record": record_id})


def open_link(view: str, instance: str, record_id: str, label: str) -> str:
    return (
        f'<td class="open"><a class="row-open" data-detail-link '
        f'href="{_e(detail_href(view, instance, record_id))}" '
        f'aria-label="{_e(label)}" title="{_e(label)}">›</a></td>'
    )


def selectors(instance_key: str, keys, values_of, with_class: bool) -> str:
    """The filter buttons over server-rendered rows (shared by both timing tables)."""
    fields = []
    if with_class:
        fields.append(
            f'<label for="lifecycle-{_e(instance_key)}-class">Class'
            f'<select id="lifecycle-{_e(instance_key)}-class" data-filter="class">'
            + "".join(
                f'<option value="{v}"{" selected" if v == "all" else ""}>{t}</option>'
                for v, t in CLASS_OPTIONS
            )
            + "</select></label>"
        )
    for key, title in keys:
        fields.append(
            f'<label for="lifecycle-{_e(instance_key)}-{key}">{title}'
            f'<select id="lifecycle-{_e(instance_key)}-{key}" data-filter="{key}">'
            '<option value="" selected>All</option>'
            + "".join(f'<option value="{_e(v)}">{_e(v)}</option>' for v in values_of(key))
            + "</select></label>"
        )
    return f'<div class="selectors lifecycle-selectors">{"".join(fields)}</div>'


def tally(count: int, history: bool) -> str:
    """The green results tally, top right, above History when there is one."""
    noun = "result" if count == 1 else "results"
    tip = "Current results (superseded excluded)" if history else "Results in this table"
    return (
        f'<div class="table-tools"><span class="tally" data-id="tally" title="{tip}">'
        f"{count} {noun}</span>"
        + (
            '<label class="history-toggle"><input type="checkbox" data-filter="history"> '
            "History (include superseded)</label>"
            if history
            else ""
        )
        + "</div>"
    )


def _render_lifecycle(snapshot):
    doc = snapshot.doc
    instance = snapshot.instance
    e = _e
    records = runtime_rows(doc)
    filters = selectors(
        instance.instance,
        FILTERS,
        lambda key: sorted({str(_row_fields(r)[key]) for r in records}),
        with_class=True,
    )
    rows = []
    for r in records:
        attrs = "".join(f' data-{k.replace("_", "-")}="{e(v)}"' for k, v in _row_fields(r).items())
        hidden = "" if default_visible(r) else " hidden"
        likelihood = r.get("likelihood") or {}
        block = r.get(PNT) if isinstance(r.get(PNT), dict) else {}
        rows.append(
            f'<tr data-record="{e(r.get("id"))}"{attrs}{hidden}>'
            f"<td>{e(likelihood.get('dataset_type'))}</td><td>{e(likelihood.get('variant'))}</td>"
            f"<td>{e(r.get('instrument'))}</td><td>{e(r.get('regime'))}</td>"
            f"<td><code>{e(setup_label(r.get('setup_id')))}</code></td>"
            f"<td>{e(r.get('host_class'))}</td>"
            f"<td>{e(variant_label(r.get('model_variant'), r.get('setup_id')))}</td>"
            + time_cell(
                runtime_s(r),
                f"per call, {block.get('per_call_source') or 'source not declared'}",
                "no vmap per-call time declared",
            )
            + time_cell(
                twelve_core_s(r),
                "producer estimate at 12 cores",
                "numba CPU setups only",
            )
            + f"<td>{e(r.get('class'))}</td>"
            + open_link("setup", instance.instance, r.get("id"), "Open this setup's details")
            + "</tr>"
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
    return (
        f'<section class="setup-browser lifecycle-browser" data-setup-browser="{e(instance.instance)}" '
        f'data-lifecycle aria-label="{e(instance.repo)} setups">'
        + filters
        + tally(visible, history=True)
        + '<div class="tablewrap"><table class="lifecycle-table"><thead><tr><th>Dataset type</th>'
        "<th>Model</th><th>Instrument</th><th>Regime</th><th>Setup</th><th>Hardware class</th>"
        "<th>Model variant</th><th class='num'>Runtime s</th><th class='num'>Est. 12-core s</th>"
        "<th>Class</th><th class='open'><span class='visually-hidden'>Details</span></th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
        f'<p class="empty" data-id="no-rows"{" hidden" if visible else ""}>'
        "No record matches this selection.</p>"
        + coverage
        + '<h4 class="extra-info">Extra Information</h4>'
        f'<p data-id="knowledge-link"><a href="{KNOWLEDGE_URL}" target="_blank" rel="noopener" '
        f'title="Opens in a new tab">{KNOWLEDGE_TITLE}</a></p>'
        "</section>"
    )


# ------------------------------------------------ v3: per-row detail pages ---

SIBLING_KEY = ("instrument", "setup_id", "host_class", "model_variant", "regime")
PANELS = (
    ("runtime", "Likelihood runtime"),
    ("breakdown", "Likelihood breakdown"),
    ("compile", "Compilation and setup"),
    ("memory_host", "Memory (host)"),
    ("memory_device", "Memory (device)"),
    ("parity", "Parity"),
)


def sibling_key(record) -> str:
    """The cell a record belongs to: likelihood, instrument, setup, hardware, variant, regime."""
    return json.dumps(
        [record.get("likelihood"), *(record.get(k) for k in SIBLING_KEY)], sort_keys=True
    )


def _fmt(value, unit) -> str:
    """Four significant figures in the record's own unit (display only)."""
    return f"{value:.4g} {unit}" if _real(value) else "—"


def _metric_label(name: str) -> str:
    return name.removeprefix("steps.")


def _metric_panel(records, title, axis) -> str:
    """One metric-panel of the old setup page: a bar per value within each record."""
    e = _e
    if not records:
        return (
            f'<details class="metric-panel" data-axis="{axis}"><summary>{e(title)}</summary>'
            f'<p class="empty">No {e(title.lower())} recorded for this setup.</p></details>'
        )
    parts = [f'<details class="metric-panel" data-axis="{axis}" open><summary>{e(title)}</summary>']
    for r in records:
        values = {k: v for k, v in (r.get("values") or {}).items() if _real(v)}
        unit = r.get("unit")
        total = values.get("component_total") if axis == "breakdown" else None
        scale = "component total" if total else "largest value"
        denominator = total or max((abs(v) for v in values.values()), default=0)
        caption = f"{scale.capitalize()} · {unit} · {r.get('status')} · measured " + str(
            r.get("measured_at") or "—"
        )
        if axis == "parity":
            parts.append(
                f"<p class='metric-meta scale-caption'>{e(unit)} · {e(r.get('status'))}</p>"
            )
            parts.append(
                '<dl class="config">'
                + "".join(
                    f"<dt>{e(_metric_label(k))}</dt><dd><strong class='metric-value' "
                    f"title='{e(v)}'>{e(f'{v:.4g}')}</strong></dd>"
                    for k, v in values.items()
                )
                + "</dl>"
            )
            continue
        parts.append(
            f"<p class='metric-meta scale-caption'>{e(caption)}</p><ul class='metric-list'>"
        )
        ordered = sorted(values.items(), key=lambda kv: (kv[0] != "component_total", -kv[1]))
        for k, v in ordered:
            width = min(100.0, 100 * abs(v) / denominator) if denominator else 0
            kind = " data-kind='total'" if k == "component_total" else ""
            parts.append(
                f"<li class='metric-row' data-metric='{e(k)}'{kind}>"
                f"<div class='metric-title'><span>{e(_metric_label(k))}</span>"
                f"<strong class='metric-value' title='Exact recorded value: {e(v)} {e(unit)}'>"
                f"{e(_fmt(v, unit))}</strong></div>"
                f"<div class='bar-track' aria-hidden='true'><div class='bar' "
                f"style='width:{width:.1f}%' data-scale='{e(scale)}'></div></div></li>"
            )
        parts.append("</ul>")
    parts.append("</details>")
    return "".join(parts)


def _dl(pairs) -> str:
    return (
        '<dl class="config">'
        + "".join(f"<dt>{_e(k)}</dt><dd>{v}</dd>" for k, v in pairs if v not in (None, "", "None"))
        + "</dl>"
    )


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return _e("; ".join(str(v) for v in value))
    return _e(value)


def _headline(label, value_html, note="") -> str:
    note_html = f"<span class='headline-note'>{_e(note)}</span>" if note else ""
    return (
        f"<div class='headline-row'><dt>{_e(label)}</dt><dd>"
        f"<strong class='headline-value'>{value_html}</strong>{note_html}</dd></div>"
    )


def _seconds(value, missing="not recorded") -> str:
    shown = fixed(value)
    return f"<span title='{_e(value)} s'>{shown} s</span>" if shown else _e(missing)


def detail_title(project: str, record) -> str:
    likelihood = record.get("likelihood") or {}
    return " / ".join(
        str(x)
        for x in (
            project,
            likelihood.get("dataset_type"),
            likelihood.get("variant"),
            record.get("instrument"),
            setup_label(record.get("setup_id")),
            record.get("host_class"),
            variant_label(record.get("model_variant"), record.get("setup_id")),
        )
    )


def detail_page(snapshot, record, siblings, back: str, project: str) -> str:
    """The old per-setup page, server-rendered for one runtime row (hidden until routed)."""
    e = _e
    instance = snapshot.instance
    title = detail_title(project, record)
    values = record.get("values") or {}
    block = record.get(PNT) if isinstance(record.get(PNT), dict) else {}
    kind, node_text, node_detail = node_throughput(record)
    node_html = e(node_text) + (
        " <span class='projected-badge'>projected</span>" if kind == "projected" else ""
    )
    headline = [
        _headline(
            "Runtime (vmap per call)",
            _seconds(runtime_s(record), "no vmap per-call time declared"),
            f"Producer: projected_node_throughput.per_call_s from "
            f"{block.get('per_call_source') or 'an undeclared source'}",
        )
    ]
    for metric in ("single_jit_median", "single_jit_block", "vmap.per_call", "vmap.batch_time"):
        if metric in values:
            headline.append(_headline(metric, _seconds(values[metric])))
    est = (
        record.get("estimated_12_core") if isinstance(record.get("estimated_12_core"), dict) else {}
    )
    headline.append(
        _headline(
            "Est. 12-core",
            _seconds(twelve_core_s(record), "numba CPU setups only"),
            (est.get("ruling") or "") if est else "",
        )
    )
    headline.append(_headline("Node throughput", node_html, node_detail))
    same = [r for r in siblings if r.get("status") == record.get("status") and r is not record]
    panels = []
    for axis, panel_title in PANELS:
        rows = [record] if axis == "runtime" else [r for r in same if r.get("measurement") == axis]
        if axis == "memory_device" and not rows:
            continue
        panels.append(_metric_panel(rows, panel_title, axis))
    validation = record.get("validation") or {}
    status = _dl(
        [
            ("Class", _text(record.get("class"))),
            ("Status", _text(record.get("status"))),
            ("Decision", _text(record.get("decision_id") or "—")),
            (
                "Validation",
                _text(
                    f"{validation.get('status')}: {validation.get('reason')}"
                    if validation
                    else None
                ),
            ),
            ("Limitations", _text(record.get("limitations"))),
            ("Superseded by", _text(record.get("superseded_by"))),
            ("Regime", _text(record.get("regime"))),
            ("Release pin", _text(record.get("release_pin"))),
            ("Measured on release", _text(record.get("measured_release_pin"))),
            ("Measured at", _text(record.get("measured_at"))),
            ("Run", f"<code>{_text(record.get('run_id'))}</code>"),
            ("Record", f"<code>{_text(record.get('id'))}</code>"),
        ]
    )
    identity = record.get("identity") or {}
    resources = record.get("resources") or {}
    setup = record.get("setup") or {}
    config = _dl(
        [("Setup id", f"<code>{_text(record.get('setup_id'))}</code>")]
        + [(f"Setup {k}", _text(v)) for k, v in setup.items()]
        + [
            ("Device", _text(identity.get("device"))),
            ("Backend", _text(identity.get("backend"))),
            ("Precision", _text(identity.get("precision"))),
            ("Library version", _text(identity.get("library_version"))),
            ("Host", _text((record.get("provenance") or {}).get("host"))),
            ("CPUs per evaluation", _text(resources.get("cpus_per_eval"))),
            ("Peak RSS (GB)", _text(resources.get("peak_rss_gb"))),
            ("Resources note", _text(resources.get("reason"))),
        ]
    )
    links = {}
    for r in [record, *same]:
        ev = r.get("evidence") or {}
        if ev.get("path"):
            links.setdefault(ev["path"], f"{r.get('measurement')} evidence")
        for fig in r.get("figures") or []:
            links.setdefault(fig["path"], f"{fig.get('kind')} figure")
    evidence = "".join(
        f'<li><a href="{e(instance.blob_url(snapshot.commit, quote(path, safe="/")))}">'
        f"{e(label)}</a> <code>{e(path)}</code></li>"
        for path, label in links.items()
    )
    history = sorted(
        (r for r in siblings if r.get("measurement") == "runtime"),
        key=lambda r: str(r.get("measured_at") or ""),
        reverse=True,
    )
    history_items = "".join(
        "<li>"
        + (
            f"<b>{e(r.get('status'))}</b> (this page)"
            if r is record
            else f'<a data-detail-link href="{e(detail_href("setup", instance.instance, r.get("id")))}">'
            f"{e(r.get('status'))}</a>"
        )
        + f" · measured {e(r.get('measured_at') or '—')} · runtime "
        f"{e(fixed(runtime_s(r)) or '—')} s · <code>{e(r.get('id'))}</code></li>"
        for r in history
    )
    return (
        f'<article class="detail-page" data-view="setup" data-instance="{e(instance.instance)}" '
        f'data-record="{e(record.get("id"))}" data-title="{e(title)}" hidden>'
        f'<a class="back-link" data-detail-link data-back href="{e(back)}">← Profiling Timings</a>'
        f"<h2>{e(title)}</h2>"
        f"<p class='metric-meta'>Regime {e(record.get('regime'))} · class {e(record.get('class'))} · "
        f"status {e(record.get('status'))} · measured {e(record.get('measured_at') or '—')}</p>"
        f'<section class="headline-metrics" aria-label="Headline timings"><dl class="headline-list">'
        + "".join(headline)
        + "</dl></section>"
        + "".join(panels)
        + '<details class="metric-panel" data-axis="status" open><summary>Status, decision and '
        "validation</summary>" + status + "</details>"
        '<details class="metric-panel" data-axis="configuration"><summary>Configuration</summary>'
        + config
        + "</details>"
        '<details class="metric-panel" data-axis="evidence" open><summary>Evidence</summary>'
        f'<ul class="evidence-list">{evidence or "<li>No evidence recorded.</li>"}</ul></details>'
        '<details class="metric-panel" data-axis="history" open><summary>History</summary>'
        f'<ul class="evidence-list">{history_items}</ul></details>'
        "</article>"
    )


def detail_pages(snapshot, back: str, project: str) -> str:
    """One hidden detail page per table row of a v3 capture (empty for other versions)."""
    doc = snapshot.doc or {}
    if not lifecycle(doc):
        return ""
    by_key: dict[str, list] = {}
    for r in doc.get("records") or []:
        if isinstance(r, dict):
            by_key.setdefault(sibling_key(r), []).append(r)
    return "".join(
        detail_page(snapshot, r, by_key.get(sibling_key(r), [r]), back, project)
        for r in runtime_rows(doc)
    )


def page_ids(snapshot) -> set[str]:
    """The record ids that have a detail page in this capture."""
    return {r.get("id") for r in runtime_rows(snapshot.doc)} if lifecycle(snapshot.doc) else set()


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


def _md_time(value) -> str:
    shown = fixed(value)
    return f"**{shown}**" if shown is not None else "—"


def _markdown_lifecycle(snapshot):
    doc = snapshot.doc
    name = snapshot.instance.repo.removesuffix("_profiling")
    current = [r for r in runtime_rows(doc) if default_visible(r)]
    lines = [
        f"<details><summary>{html.escape(name)} — current runtime setups</summary>",
        "",
        f"[Interactive setup browser]({snapshot.instance.dashboard_url})",
        "",
        f"{len(current)} current result{'' if len(current) == 1 else 's'}.",
        "",
        "| Dataset type | Model | Instrument | Regime | Setup | Hardware class | Model variant "
        "| Runtime s | Est. 12-core s | Class |",
        "|---|---|---|---|---|---|---|---:|---:|---|",
    ]
    esc = lambda v: html.escape(str(v)).replace("|", "\\|")  # noqa: E731
    for r in current:
        likelihood = r.get("likelihood") or {}
        lines.append(
            f"| {esc(likelihood.get('dataset_type'))} | {esc(likelihood.get('variant'))} "
            f"| {esc(r.get('instrument'))} | {esc(r.get('regime'))} "
            f"| `{esc(setup_label(r.get('setup_id')))}` | {esc(r.get('host_class'))} "
            f"| {esc(variant_label(r.get('model_variant'), r.get('setup_id')))} "
            f"| {_md_time(runtime_s(r))} | {_md_time(twelve_core_s(r))} | {esc(r.get('class'))} |"
        )
    missing = not_measured(doc)
    lines += ["", f"Coverage: {len(missing)} optimal cell(s) not measured.", ""]
    lines += [f"- {esc(_cell_label(c))}" for c in missing]
    lines += ["", "#### Extra Information", "", f"[{KNOWLEDGE_TITLE}]({KNOWLEDGE_URL})"]
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
