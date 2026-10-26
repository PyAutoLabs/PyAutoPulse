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
