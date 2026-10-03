"""Build the board (``dashboard.md`` + ``dashboard.html``, plus ``badge.json`` and
the ``state.json`` organ-cockpit feed) from the ingested snapshots.

The campaign control room comes first. The evidence section has one row per registered project: scope, evidence time,
last fetch (with the resolved commit), coverage, and three separate columns
for the three notions the spec keeps apart — **integrity** (transport and
schema: ok / invalid / unavailable / unsupported / cached), **freshness**
(``valid_until``; when the producer declares none, "freshness policy
unspecified" with the evidence's age at fetch, never an invented TTL) and
**qualification** (how many records and comparisons the producer itself marks
qualified). Then one detail section per instance shows the producer's own
``limitations[]`` verbatim, its refused (excluded) rows, and its own
``comparisons[]`` grouped by hardware identity, each with links to its two
records' evidence at the captured commit and a ``/profiling triage <key>``
manual handoff. Pairs the reader refuses (axis mismatch, changed hardware,
missing endpoint) are listed apart with the reason and no ratio.

The board never recomputes a ratio, never combines records whose axis or
hardware differs, never ranks cells across projects and never emits a
release verdict. Its output is deterministic: the pages carry no wall-clock
stamp (every time shown comes from a receipt or snapshot) and ``state.json``'s
``updated`` moves only when the feed's content does.
"""

from __future__ import annotations

import html
import json
import re
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path

from pulse import ORGAN_ROOT, campaigns
from pulse import summary as summary_mod
from pulse.ingest import Snapshot

PAGES_URL = "https://pyautolabs.github.io/PyAutoPulse/"
REPO_URL = "https://github.com/PyAutoLabs/PyAutoPulse"
STATE_SCHEMA_VERSION = 1  # the organ-cockpit feed contract (PyAutoBrain/board/state_schema.json)
FRESHNESS_DAYS = 90  # presentation only: when an unspecified-policy feed is called out
MARKER = re.compile(r"<!-- pulse:instance name=(\S+) receipt=(\S+) outcome=(\S+) shown=(\S+) -->")


# ------------------------------------------------------------- per view ---


def _short(sha: str | None) -> str:
    return sha[:8] if sha else "—"


def _date(stamp: str | None) -> str:
    return stamp[:10] if isinstance(stamp, str) else "—"


def _days(later: str | None, earlier: str | None) -> int | None:
    a, b = summary_mod.parse_utc(later), summary_mod.parse_utc(earlier)
    if a is None or b is None:
        return None
    return max(0, (a - b).days)


def records(s: Snapshot) -> list[dict]:
    return list((s.doc or {}).get("records") or [])


def comparisons(s: Snapshot) -> list[dict]:
    return list((s.doc or {}).get("comparisons") or [])


def pairs(s: Snapshot) -> list[summary_mod.Pair]:
    return summary_mod.pair(s.doc) if s.doc else []


def integrity(s: Snapshot) -> str:
    """Transport + schema integrity of the latest read."""
    if s.source == "local":
        dirty = {True: "dirty", False: "clean", None: "state unknown"}[s.dirty]
        where = f"local checkout {_short(s.commit)} ({dirty})"
        return where if not s.failed else f"{s.outcome} · {where}"
    if not s.failed:
        return "ok"
    if s.cached:
        return f"cached · latest fetch {s.outcome}"
    return s.outcome


def evidence(s: Snapshot) -> str:
    if not s.doc:
        return "—"
    ev = s.doc.get("evidence_updated_at")
    if ev is None:
        return f"unknown ({s.doc.get('evidence_updated_at_reason') or 'no reason given'})"
    return _date(ev)


def freshness(s: Snapshot, now: str | None = None) -> str:
    """Evidence freshness against the producer's own policy, never a global TTL."""
    if not s.doc:
        return "—"
    ev = s.doc.get("evidence_updated_at")
    vu = s.doc.get("valid_until")
    if vu is not None:
        if now is not None and summary_mod.parse_utc(now) > summary_mod.parse_utc(vu):
            return f"stale (valid_until {_date(vu)} passed)"
        return f"valid until {_date(vu)}"
    if ev is None:
        return "freshness policy unspecified · evidence time unknown"
    age = _days(s.fetched_at, ev)
    at = f" at fetch {_date(s.fetched_at)}" if s.fetched_at else ""
    aged = f"age {age} d{at}" if age is not None else "age unknown"
    return f"freshness policy unspecified · {aged}"


def qualification(s: Snapshot) -> str:
    """The producer's own qualification flags, counted, never upgraded."""
    if not s.doc:
        return "—"
    recs, comps = records(s), comparisons(s)
    if not recs:
        return "no measurements"
    q = summary_mod.qualified_records(s.doc)
    cq = sum(1 for c in comps if c.get("qualified") is True)
    return f"{q}/{len(recs)} records · {cq}/{len(comps)} comparisons qualified"


def coverage(s: Snapshot) -> str:
    if not s.doc:
        return "—"
    if not records(s):
        return "no measurements"
    cov = s.doc.get("coverage") or {}
    obs = cov.get("observed") or {}
    parts = [f"{v} {k}" for k, v in obs.items()]
    parts.append(f"{len(cov.get('excluded') or [])} excluded")
    return " · ".join(parts)


def last_fetch(s: Snapshot) -> str:
    if s.source == "local":
        return f"local read · {_short(s.commit)}"
    if s.fetched_at is None and s.attempt_at is None:
        return "never"
    if s.cached:
        return f"{_date(s.fetched_at)} @ {_short(s.commit)} (attempt {_date(s.attempt_at)} failed)"
    if s.doc:
        return f"{_date(s.fetched_at)} @ {_short(s.commit)}"
    return f"attempt {_date(s.attempt_at)} failed"


def drifted(s: Snapshot) -> list[summary_mod.Pair]:
    return [p for p in pairs(s) if not p.refused and p.comparison.get("status") == "drifted"]


def triage_line(p: summary_mod.Pair) -> str:
    return f"/profiling triage {p.key}"


def receipt_url(s: Snapshot) -> str:
    return f"{REPO_URL}/blob/main/receipts/{s.instance.instance}.json"


def counts(views) -> list[tuple[str, int]]:
    """The head-of-page counts a cockpit strip can read."""
    return [
        ("Projects", len(views)),
        ("Records", sum(len(records(s)) for s in views)),
        ("Comparisons", sum(len(comparisons(s)) for s in views)),
        ("Drifted", sum(len(drifted(s)) for s in views)),
        ("Refused pairs", sum(sum(1 for p in pairs(s) if p.refused) for s in views)),
        ("Cached", sum(1 for s in views if s.cached)),
        ("Failed", sum(1 for s in views if s.failed and not s.cached)),
    ]


def _grouped(s: Snapshot) -> OrderedDict[str, list[summary_mod.Pair]]:
    """Accepted pairs by hardware group, producer order kept (never ranked);
    refused pairs last."""
    groups: OrderedDict[str, list] = OrderedDict()
    for p in pairs(s):
        if not p.refused:
            groups.setdefault(p.group, []).append(p)
    refused = [p for p in pairs(s) if p.refused]
    if refused:
        groups["refused"] = refused
    return groups


def _ratio(p: summary_mod.Pair) -> str:
    if p.refused:
        return "not shown (refused)"
    r = p.comparison.get("ratio")
    return "—" if r is None else json.dumps(r)


def _endpoint(s: Snapshot, p: summary_mod.Pair, end: str) -> tuple[str, str | None]:
    """(label, evidence URL at the captured commit) for one endpoint."""
    ref = p.comparison.get(end)
    rec = getattr(p, end)
    if ref is None:
        return "—", None
    if rec is None:
        return str(ref), None
    ev = rec.get("evidence") or {}
    url = s.instance.blob_url(s.commit, ev["path"])
    frag = ev.get("fragment")
    return (f"{ref} [{frag}]" if frag else str(ref)), url


def marker(s: Snapshot) -> str:
    receipt = s.attempt_commit or "none"
    shown = s.commit or "none"
    return (
        f"<!-- pulse:instance name={s.instance.instance} receipt={receipt} "
        f"outcome={s.outcome} shown={shown} -->"
    )


def markers(text: str) -> dict[str, dict]:
    """``{instance: {receipt, outcome, shown}}`` as recorded in a dashboard.md."""
    return {
        name: {"receipt": receipt, "outcome": outcome, "shown": shown}
        for name, receipt, outcome, shown in MARKER.findall(text or "")
    }


# ------------------------------------------------------------- markdown ---

LEDE = (
    "The cross-project view of the organism's profiling. Each `<lib>_profiling` project repo "
    "runs its producers, keeps its results and drift policy, and publishes a "
    "`profiling-summary` file. This page reads each file at one resolved commit, validates the "
    "exchange contract and shows what the producer says: it recomputes no ratio, combines no "
    "timings whose axis or hardware differs, ranks nothing across projects and issues no "
    "verdict. Judgment belongs to the Brain's profiling conductor (`/profiling triage`)."
)
NOTIONS = (
    "Three notions are kept apart: **integrity** is whether the file was fetched and meets the "
    "contract; **freshness** is the evidence's age against the producer's own `valid_until` "
    '(none declared → "freshness policy unspecified"); **qualification** is the producer\'s own '
    "flag on each record and comparison. Healthy transport never makes unknown quality green."
)


def _md_escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _status_lines(s: Snapshot, now: str | None = None) -> list[str]:
    inst = s.instance
    out = []
    if s.source == "local":
        out.append(
            f"**Local read:** `{Path(s.checkout or '?').name}` at `{_short(s.commit)}` "
            f"({'dirty' if s.dirty else 'clean' if s.dirty is False else 'state unknown'}) — "
            "not a published capture; no receipt written."
        )
        out.append("")
    if s.cached:
        out.append(
            f"**Cached:** showing the last good capture (commit `{_short(s.commit)}`, fetched "
            f"{s.fetched_at}, evidence {evidence(s)}). The latest fetch ({s.attempt_at}) "
            f"was **{s.outcome}**: {'; '.join(s.errors) or 'no error recorded'}."
        )
    elif s.failed:
        out.append(f"**{s.outcome.capitalize()}:** {'; '.join(s.errors) or 'no error recorded'}.")
    if s.doc:
        doc = s.doc
        pol = doc.get("comparison_policy") or {}
        rev = doc.get("producer_revision")
        out += [
            f"Project `{doc.get('project')}`, scope `{doc.get('scope')}`, read from "
            f"[{inst.github}]({inst.github_url}) `{inst.summary_path}` at "
            f"[`{_short(s.commit)}`]({inst.tree_url(s.commit)}); producer revision "
            f"`{_short(rev)}`; generated {doc.get('generated_at')}; comparison policy "
            f"`{pol.get('id')}`. [Project dashboard]({inst.dashboard_url}) · "
            f"[receipt]({receipt_url(s)}).",
            "",
            f"- **Integrity:** {integrity(s)}",
            f"- **Freshness:** {freshness(s, now)} (evidence {evidence(s)})",
            f"- **Qualification:** {qualification(s)}",
        ]
    return out


def _md_detail(s: Snapshot, now: str | None = None) -> list[str]:
    inst = s.instance
    out = ["", f"## {inst.instance}", "", marker(s), ""]
    out += _status_lines(s, now)
    if not s.doc:
        return out
    if not records(s):
        out += [
            "",
            "**No measurements.** The producer published a valid, empty feed — this is not "
            '"all measurements passed".',
        ]
    lims = s.doc.get("limitations") or []
    out += ["", f"### {inst.instance} / limitations", ""]
    out += [f"- {_md_escape(x)}" for x in lims] or ["- none declared"]
    excluded = (s.doc.get("coverage") or {}).get("excluded") or []
    if excluded:
        out += ["", f"### {inst.instance} / excluded by the producer", ""]
        for x in excluded:
            ev = x.get("evidence") or {}
            out.append(
                f"- `{x.get('id')}`: {_md_escape(x.get('reason'))} "
                f"([evidence]({inst.blob_url(s.commit, ev.get('path'))}))"
            )
    for group, items in _grouped(s).items():
        title = (
            "refused by the reader (never combined)"
            if group == "refused"
            else f"comparisons on {group}"
        )
        out += [
            "",
            f"### {inst.instance} / {title}",
            "",
            "| Comparison | Policy | Axis · metric | Baseline → candidate | Ratio (producer) "
            "| Status | Qualified | Reasons | Triage |",
            "|---|---|---|---|---:|---|---|---|---|",
        ]
        for p in items:
            c = p.comparison
            ends = []
            for end in ("baseline", "candidate"):
                label, url = _endpoint(s, p, end)
                ends.append(f"[{label}]({url})" if url else label)
            reasons = "; ".join(list(c.get("reasons") or []) + p.refused) or "—"
            out.append(
                f"| `{_md_escape(p.key)}` | {c.get('policy')} | {c.get('axis')} · "
                f"{c.get('metric')} | {' → '.join(ends)} | {_ratio(p)} | {c.get('status')} | "
                f"{'yes' if c.get('qualified') else 'no'} | {_md_escape(reasons)} | "
                f"`{triage_line(p)}` |"
            )
    return out


def render_markdown(views, now: str | None = None, campaign_data: dict | None = None) -> str:
    now = now or _utc_now()
    out = [
        "# PyAutoPulse — profiling dashboard",
        "",
        "<!-- Generated by `bin/pyauto-pulse board` from registry.yaml, receipts/ and "
        "snapshots/. Do not edit by hand. -->",
        "",
        campaigns.markdown(campaign_data if campaign_data is not None else campaigns.load()),
        LEDE,
        f"Live page: [{PAGES_URL}]({PAGES_URL}).",
        "",
        "| Where | Count |",
        "|-------|------:|",
        *[f"| [{label}](#projects) | {n} |" for label, n in counts(views)],
        "",
        "## Projects",
        "",
        "| Project | Scope | Evidence | Last fetch | Coverage | Integrity | Freshness "
        "| Qualification | Links |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in views:
        inst = s.instance
        scope = (s.doc or {}).get("scope") or "—"
        out.append(
            f"| [{inst.instance}](#{inst.instance}) ({inst.repo}) | {scope} | {evidence(s)} | "
            f"{last_fetch(s)} | {coverage(s)} | {integrity(s)} | {freshness(s, now)} | "
            f"{qualification(s)} | [dashboard]({inst.dashboard_url}) · "
            f"[repo]({inst.github_url}) · [receipt]({receipt_url(s)}) |"
        )
    out += ["", NOTIONS]
    for s in views:
        out += _md_detail(s, now)
    return "\n".join(out).rstrip("\n") + "\n"


# ----------------------------------------------------------------- html ---

CSS = """
:root{--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--card:#f6f8fa;--line:#d1d9e0;
--accent:#0b7a4b;--hero1:#062b1c;--hero2:#000000;--glow:#2ee88f;--ok:#1a7f37;--warn:#9a6700;
--bad:#cf222e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d1117;--fg:#e6edf3;
--muted:#9198a1;--card:#151b23;--line:#3d444d;--accent:#34d399;--ok:#3fb950;--warn:#d29922;
--bad:#f85149}}
:root[data-theme="dark"]{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--card:#151b23;
--line:#3d444d;--accent:#34d399;--ok:#3fb950;--warn:#d29922;--bad:#f85149}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1200px;margin:0 auto;padding:0 16px 48px}
.hero{background:radial-gradient(circle at 30% 20%,var(--hero1),var(--hero2));color:#fff;
padding:28px 16px 22px;text-align:center}
.hero h1{margin:0;font-size:28px;letter-spacing:.5px}.hero h1 span{color:var(--glow)}
.hero p{margin:6px 0 0;color:#bfe9d3;font-size:13px;letter-spacing:2px;text-transform:uppercase}
h2,h3{color:var(--accent)}h2{border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:32px}
a{color:var(--accent)}
.lede{color:var(--muted)}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
td.num{text-align:right;white-space:nowrap}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.muted{color:var(--muted)}
.notions{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin:8px 0}
.notions div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px}
.notions b{display:block;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}
.stats{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}
.stats div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px}
.stats b{display:block;font-size:20px;color:var(--accent)}.stats span{font-size:12px;color:var(--muted)}
button[data-copy]{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;text-align:left;
background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;
padding:3px 6px;cursor:pointer;word-break:break-all}
button.copied{border-color:var(--ok)}
.checkin textarea{display:block;width:100%;font:inherit;font-size:14px;line-height:1.5;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:12px;margin:8px 0;resize:vertical}
#copy-checkin{background:var(--accent);color:var(--bg);border:0;border-radius:6px;padding:10px 16px;cursor:pointer;font-weight:600}
#copy-status{margin-left:12px}
code{color:var(--accent);word-break:break-all}
"""

JS = """
var copyCheckin=document.getElementById('copy-checkin');
if(copyCheckin){copyCheckin.addEventListener('click',async function(){
  var field=document.getElementById('checkin-prompt'), status=document.getElementById('copy-status');
  try {
    if(navigator.clipboard && window.isSecureContext){await navigator.clipboard.writeText(field.value)}
    else {field.focus();field.select();if(!document.execCommand('copy')){throw new Error('copy unavailable')}}
    status.textContent='Copied';
  } catch(error){field.focus();field.select();status.textContent='Select and copy the prompt above.'}
});}

document.querySelectorAll('button[data-copy]').forEach(function(b){
  b.addEventListener('click',function(){
    var t=b.getAttribute('data-copy');
    var done=function(){b.classList.add('copied');setTimeout(function(){b.classList.remove('copied')},1200)};
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,function(){})}
  });
});
document.querySelectorAll('[data-age-from]').forEach(function(el){
  var t=Date.parse(el.getAttribute('data-age-from'));
  if(!isNaN(t)){el.textContent=' · '+Math.max(0,Math.floor((Date.now()-t)/864e5))+' d today';}
});
"""


def _e(value) -> str:
    return html.escape(str(value), quote=True)


def _integrity_class(s: Snapshot) -> str:
    if not s.failed:
        return "ok" if s.source == "remote" else "warn"
    return "warn" if s.cached else "bad"


def _html_notions(s: Snapshot, now: str | None = None) -> str:
    ev = (s.doc or {}).get("evidence_updated_at")
    live = f"<span class='muted' data-age-from='{_e(ev)}'></span>" if ev else ""
    return (
        "<div class='notions'>"
        f"<div><b>Integrity</b><span class='{_integrity_class(s)}'>{_e(integrity(s))}</span></div>"
        f"<div><b>Freshness</b>{_e(freshness(s, now))} (evidence {_e(evidence(s))}){live}</div>"
        f"<div><b>Qualification</b>{_e(qualification(s))}</div>"
        "</div>"
    )


def _html_detail(s: Snapshot, now: str | None = None) -> str:
    inst = s.instance
    parts = [f"<h2 id='{_e(inst.instance)}'>{_e(inst.instance)} · {_e(inst.repo)}</h2>"]
    if s.source == "local":
        parts.append(
            f"<p class='warn'>Local read of <code>{_e(Path(s.checkout or '?').name)}</code> at "
            f"<code>{_e(_short(s.commit))}</code> "
            f"({'dirty' if s.dirty else 'clean' if s.dirty is False else 'state unknown'}): "
            "not a published capture; no receipt written.</p>"
        )
    if s.cached:
        parts.append(
            f"<p class='warn'><b>Cached:</b> last good capture at "
            f"<code>{_e(_short(s.commit))}</code>, fetched {_e(s.fetched_at)}, evidence "
            f"{_e(evidence(s))}. Latest fetch ({_e(s.attempt_at)}) was <b>{_e(s.outcome)}</b>: "
            f"{_e('; '.join(s.errors) or 'no error recorded')}.</p>"
        )
    elif s.failed:
        parts.append(
            f"<p class='bad'><b>{_e(s.outcome)}:</b> {_e('; '.join(s.errors) or 'no error')}</p>"
        )
    if not s.doc:
        return "".join(parts)
    doc = s.doc
    pol = doc.get("comparison_policy") or {}
    parts.append(
        f"<p class='lede'>Project <code>{_e(doc.get('project'))}</code>, scope "
        f"<code>{_e(doc.get('scope'))}</code>, read from <a href='{_e(inst.github_url)}'>"
        f"{_e(inst.github)}</a> <code>{_e(inst.summary_path)}</code> at "
        f"<a href='{_e(inst.tree_url(s.commit))}'><code>{_e(_short(s.commit))}</code></a>; "
        f"producer revision <code>{_e(_short(doc.get('producer_revision')))}</code>; generated "
        f"{_e(doc.get('generated_at'))}; policy <code>{_e(pol.get('id'))}</code>. "
        f"<a href='{_e(inst.dashboard_url)}'>Project dashboard</a> · "
        f"<a href='{_e(receipt_url(s))}'>receipt</a>.</p>"
    )
    parts.append(_html_notions(s, now))
    if not records(s):
        parts.append(
            "<p class='warn'><b>No measurements.</b> A valid, empty feed — not "
            "“all measurements passed”.</p>"
        )
    lims = doc.get("limitations") or []
    parts.append("<h3>Limitations (the producer's own)</h3><ul>")
    parts += [f"<li>{_e(x)}</li>" for x in lims] or ["<li>none declared</li>"]
    parts.append("</ul>")
    excluded = (doc.get("coverage") or {}).get("excluded") or []
    if excluded:
        parts.append("<h3>Excluded by the producer</h3><ul>")
        for x in excluded:
            ev = x.get("evidence") or {}
            parts.append(
                f"<li><code>{_e(x.get('id'))}</code>: {_e(x.get('reason'))} "
                f"(<a href='{_e(inst.blob_url(s.commit, ev.get('path')))}'>evidence</a>)</li>"
            )
        parts.append("</ul>")
    for group, items in _grouped(s).items():
        title = (
            "Refused by the reader (never combined)"
            if group == "refused"
            else f"Comparisons on {group}"
        )
        rows = []
        for p in items:
            c = p.comparison
            ends = []
            for end in ("baseline", "candidate"):
                label, url = _endpoint(s, p, end)
                ends.append(f"<a href='{_e(url)}'>{_e(label)}</a>" if url else _e(label))
            reasons = "; ".join(list(c.get("reasons") or []) + p.refused) or "—"
            line = triage_line(p)
            rows.append(
                f"<tr><td><code>{_e(p.key)}</code></td><td>{_e(c.get('policy'))}</td>"
                f"<td>{_e(c.get('axis'))} · {_e(c.get('metric'))}</td><td>{' → '.join(ends)}</td>"
                f"<td class='num'>{_e(_ratio(p))}</td><td>{_e(c.get('status'))}</td>"
                f"<td>{'yes' if c.get('qualified') else 'no'}</td><td>{_e(reasons)}</td>"
                f"<td><button type='button' data-copy='{_e(line)}' "
                f"title='Copy the manual handoff'>{_e(line)}</button></td></tr>"
            )
        parts.append(
            f"<h3>{_e(title)}</h3><div class='tablewrap'><table><thead><tr><th>Comparison</th>"
            "<th>Policy</th><th>Axis · metric</th><th>Baseline → candidate</th>"
            "<th>Ratio (producer)</th><th>Status</th><th>Qualified</th><th>Reasons</th>"
            f"<th>Triage</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
        )
    return "".join(parts)


def render_html(views, now: str | None = None, campaign_data: dict | None = None) -> str:
    now = now or _utc_now()
    rows = []
    for s in views:
        inst = s.instance
        rows.append(
            f"<tr><td><a href='#{_e(inst.instance)}'>{_e(inst.instance)}</a> "
            f"<span class='muted'>{_e(inst.repo)}</span></td>"
            f"<td>{_e((s.doc or {}).get('scope') or '—')}</td><td>{_e(evidence(s))}</td>"
            f"<td>{_e(last_fetch(s))}</td><td>{_e(coverage(s))}</td>"
            f"<td class='{_integrity_class(s)}'>{_e(integrity(s))}</td>"
            f"<td>{_e(freshness(s, now))}</td><td>{_e(qualification(s))}</td>"
            f"<td><a href='{_e(inst.dashboard_url)}'>dashboard</a> · "
            f"<a href='{_e(inst.github_url)}'>repo</a> · "
            f"<a href='{_e(receipt_url(s))}'>receipt</a></td></tr>"
        )
    tiles = "".join(f"<div><b>{n}</b><span>{_e(label)}</span></div>" for label, n in counts(views))
    lede = _e(LEDE).replace("`/profiling triage`", "<code>/profiling triage</code>")
    lede = re.sub(r"`(.+?)`", r"<code>\1</code>", lede)
    notions = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", _e(NOTIONS))
    notions = re.sub(r"`(.+?)`", r"<code>\1</code>", notions)
    return (
        "<!doctype html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>PyAutoPulse dashboard</title>"
        "<!-- Generated by `bin/pyauto-pulse board`. Do not edit by hand. -->"
        f"<style>{CSS}</style></head><body>"
        "<header class='hero'><h1>PyAuto<span>Pulse</span></h1>"
        "<p>Measure. Trace. Compare.</p></header>"
        f"<main>{campaigns.render_html(campaign_data if campaign_data is not None else campaigns.load())}"
        f"<p class='lede'>{lede}</p>"
        f"<div class='stats'>{tiles}</div>"
        "<h2 id='projects'>Projects</h2>"
        "<div class='tablewrap'><table><thead><tr><th>Project</th><th>Scope</th>"
        "<th>Evidence</th><th>Last fetch</th><th>Coverage</th><th>Integrity</th>"
        "<th>Freshness</th><th>Qualification</th><th>Links</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        f"<p class='muted'>{notions}</p>"
        f"{''.join(_html_detail(s, now) for s in views)}</main><script>{JS}</script></body></html>\n"
    )


# ---------------------------------------------------------- badge, state ---


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def headline(views) -> str:
    n = len(views)
    recs = sum(len(records(s)) for s in views)
    cached = sum(1 for s in views if s.cached)
    failed = sum(1 for s in views if s.failed and not s.cached)
    text = f"{n} project{'' if n == 1 else 's'} · {recs} records · {cached} cached"
    if failed:
        text += f" · {failed} failed"
    return text


def _one_line(text: str, limit: int = 300) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _instance_items(s: Snapshot, now: str) -> tuple[list, list, list]:
    inst = s.instance
    key = inst.instance
    red, yellow, info = [], [], []
    fetch_action = {
        "id": "fetch",
        "label": "Re-fetch this instance",
        "kind": "command",
        "target": f"bin/pyauto-pulse fetch --instance {key}",
        "safety": "read_only",
    }
    open_action = {
        "id": "open",
        "label": "Open the project dashboard",
        "kind": "link",
        "target": inst.dashboard_url,
        "safety": "read_only",
    }
    if s.failed:
        why = _one_line("; ".join(s.errors) or "no error recorded", 200)
        if s.cached and s.outcome == "unavailable":
            yellow.append(
                {
                    "id": f"pulse:{key}:cached",
                    "severity": "yellow",
                    "state": "stale",
                    "text": _one_line(
                        f"{key}: fetch unavailable; showing cached capture "
                        f"{_short(s.commit)} from {s.fetched_at}"
                    ),
                    "reason": why,
                    "url": receipt_url(s),
                    "prompt": None,
                    "actions": [fetch_action, open_action],
                }
            )
        else:
            tail = f"; showing cached capture {_short(s.commit)}" if s.cached else ""
            red.append(
                {
                    "id": f"pulse:{key}:{s.outcome}",
                    "severity": "red",
                    "state": "failed",
                    "text": _one_line(f"{key}: summary {s.outcome}{tail}"),
                    "reason": why,
                    "url": receipt_url(s),
                    "prompt": None,
                    "actions": [fetch_action, open_action],
                }
            )
    if not s.doc:
        return red, yellow, info
    doc = s.doc
    ev, vu = doc.get("evidence_updated_at"), doc.get("valid_until")
    if vu is not None and summary_mod.parse_utc(now) > summary_mod.parse_utc(vu):
        yellow.append(
            {
                "id": f"pulse:{key}:stale",
                "severity": "yellow",
                "state": "stale",
                "text": f"{key}: evidence stale (valid_until {_date(vu)} passed)",
                "url": inst.dashboard_url,
                "prompt": None,
                "actions": [open_action],
            }
        )
    elif vu is None and ev is not None and (_days(now, ev) or 0) > FRESHNESS_DAYS:
        yellow.append(
            {
                "id": f"pulse:{key}:aged",
                "severity": "yellow",
                "state": "stale",
                "text": (
                    f"{key}: evidence from {_date(ev)} is older than {FRESHNESS_DAYS} d; "
                    "freshness policy unspecified"
                ),
                "url": inst.dashboard_url,
                "prompt": None,
                "actions": [open_action],
            }
        )
    recs = records(s)
    if not recs:
        yellow.append(
            {
                "id": f"pulse:{key}:empty",
                "severity": "yellow",
                "state": "unknown",
                "text": f"{key}: no measurements (a valid, empty feed)",
                "url": inst.dashboard_url,
                "prompt": None,
                "actions": [open_action],
            }
        )
    else:
        unq = len(recs) - summary_mod.qualified_records(doc)
        if unq:
            yellow.append(
                {
                    "id": f"pulse:{key}:unqualified",
                    "severity": "yellow",
                    "state": "unknown",
                    "text": (
                        f"{key}: {unq} of {len(recs)} records unqualified "
                        "(producer provenance flags)"
                    ),
                    "url": inst.dashboard_url,
                    "prompt": None,
                    "actions": [open_action],
                }
            )
    for p in drifted(s):
        c = p.comparison
        line = triage_line(p)
        actions = [
            {
                "id": "triage",
                "label": "Hand off to profiling triage",
                "kind": "prompt",
                "target": line,
                "safety": "scientific_judgement",
            }
        ]
        if p.candidate is not None:
            actions.append(
                {
                    "id": "evidence",
                    "label": "Open the candidate's evidence",
                    "kind": "link",
                    "target": inst.blob_url(s.commit, p.candidate["evidence"]["path"]),
                    "safety": "read_only",
                }
            )
        item = {
            "id": f"pulse:{key}:drift:{p.key}",
            "severity": "yellow" if c.get("qualified") else "info",
            "state": "action_required" if c.get("qualified") else "unknown",
            "text": _one_line(
                f"{key}: {p.key} drifted (producer ratio {c.get('ratio')}, "
                f"{'qualified' if c.get('qualified') else 'unqualified: contextual flag'})"
            ),
            "reason": _one_line(
                f"{c.get('policy')} at {_short(s.commit)}: "
                + ("; ".join(c.get("reasons") or []) or "no reasons given"),
                200,
            ),
            "url": inst.dashboard_url,
            "prompt": line,
            "actions": actions,
            "recommended_action_id": "triage",
        }
        (yellow if c.get("qualified") else info).append(item)
    if s.source == "local":
        info.append(
            {
                "id": f"pulse:{key}:local",
                "severity": "info",
                "text": (
                    f"{key}: rendered from a local checkout {_short(s.commit)} "
                    f"({'dirty' if s.dirty else 'clean' if s.dirty is False else 'state unknown'})"
                ),
                "url": None,
                "prompt": None,
            }
        )
    lims = doc.get("limitations") or []
    info.append(
        {
            "id": f"pulse:{key}:census",
            "severity": "info",
            "text": (
                f"{key}: {len(recs)} records · {len(comparisons(s))} comparisons · "
                f"{len(lims)} limitations · {summary_mod.qualified_records(doc)} qualified"
            ),
            "url": inst.dashboard_url,
            "prompt": None,
        }
    )
    return red, yellow, info


def render_state(views, updated: str | None = None, now: str | None = None) -> dict:
    """The organ-cockpit feed (state.json, contract v1 in PyAutoBrain/board).

    status: red when an instance's latest read is invalid or unsupported, or
    unavailable with no cached capture; yellow when one is cached, stale
    against its own ``valid_until``, older than ``FRESHNESS_DAYS`` without a
    policy, empty, carries unqualified records, or has a qualified drift
    candidate; else green. Info rows (unqualified drift as a contextual flag,
    the census line) never move the status. This summarises the organ's own
    monitoring scope, never release readiness.
    """
    now = now or _utc_now()
    red, yellow, info = [], [], []
    for s in views:
        r, y, i = _instance_items(s, now)
        red, yellow, info = red + r, yellow + y, info + i
    status = "red" if red else "yellow" if yellow else "green"
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "organ": "pulse",
        "repo": "PyAutoPulse",
        "status": status,
        "headline": headline(views),
        "updated": updated or _utc_now(),
        "pages_url": PAGES_URL,
        "items": red + yellow + info,
    }


def render_badge(views, state: dict | None = None) -> dict:
    """The one-line headline (shields.io endpoint shape) other boards read."""
    state = state or render_state(views, updated="1970-01-01T00:00:00Z")
    color = {"red": "red", "yellow": "yellow", "green": "brightgreen"}[state["status"]]
    return {"schemaVersion": 1, "label": "pulse", "message": state["headline"], "color": color}


# --------------------------------------------------------------- output ---


def _carried_updated(path: Path, state: dict) -> str | None:
    """The committed state.json's ``updated`` when nothing else changed.

    Keeps the render deterministic (a re-render on unchanged inputs changes no
    file, so the nightly refresh commits nothing): ``updated`` moves only when
    the feed's content does.
    """
    try:
        prior = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(prior, dict) or not isinstance(prior.get("updated"), str):
        return None
    same = {k: v for k, v in prior.items() if k != "updated"} == {
        k: v for k, v in state.items() if k != "updated"
    }
    return prior["updated"] if same else None


def write(
    views, out_dir: Path = ORGAN_ROOT, updated: str | None = None, now: str | None = None
) -> list[Path]:
    out_dir = Path(out_dir)
    md, page, badge, feed = (
        out_dir / "dashboard.md",
        out_dir / "dashboard.html",
        out_dir / "badge.json",
        out_dir / "state.json",
    )
    md.write_text(render_markdown(views, now))
    page.write_text(render_html(views, now))
    state = render_state(views, updated, now)
    if updated is None:
        state["updated"] = _carried_updated(feed, state) or state["updated"]
    badge.write_text(json.dumps(render_badge(views, state), indent=2) + "\n")
    feed.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    return [md, page, badge, feed]
