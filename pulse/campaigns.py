"""Human-maintained profiling intent; never infer scientific outcomes from timings."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

from pulse import ORGAN_ROOT
from pulse.setup_browser import theme

URL = "https://github.com/PyAutoLabs/PyAutoPulse/blob/main/"
STATUSES = {
    "active",
    "ready",
    "running",
    "blocked",
    "parked",
    "needs-decision",
    "needs-slicing",
    "complete",
    "superseded",
}
CLOSED = {"complete", "superseded"}
PROMPT = (
    "Use PyAutoPulse as the home for profiling work in this ongoing chat. Read "
    "PyAutoPulse/AGENTS.md and CHECKIN.md, then the campaign ledger, relevant tasks and "
    "registered project evidence. Use Brain’s profiling conductor for profiling analysis and "
    "planning, and project-owned drivers for execution.\n\n"
    "When I give no particular direction, review every open campaign and task for changes "
    "since the last check-in: measurements, jobs, PRs, releases, blockers and recorded next "
    "steps. Give me a concise campaign-by-campaign summary and a proposed priority order. "
    "Distinguish verified updates from stale, missing or unavailable evidence.\n\n"
    "When I name a campaign, measurement, slowdown or idea, make that the main focus. Help me "
    "understand a timing result, investigate a regression, compare compatible measurements, "
    "identify missing evidence, design an experiment or develop a new campaign. Bring in "
    "related work where it affects the question; do not repeat the full campaign review on "
    "every follow-up.\n\n"
    "Make comparisons explicit about hardware, software versions, datasets, model "
    "configuration, precision and measurement method. Keep compilation and execution costs "
    "separate. Identify incompatible or incomplete comparisons rather than presenting them as "
    "evidence of improvement or regression.\n\n"
    "Discuss proposed experiments with me, explaining what each would establish and the "
    "resources it needs. Help turn agreed direction into concrete campaign tasks. Keep "
    "profiling intent and pending domain work in Pulse, execution and measurements in the "
    "project repositories, and bounded implementation work in Mind.\n\n"
    "Update the Pulse ledger with verified facts and dated source links, regenerate the board "
    "and persist changes through the repository workflow. Keep review dates separate from "
    "measurement freshness. Do not infer campaign completion or scientific acceptance from a "
    "successful job or a faster timing alone.\n\n"
    "Carry clearly authorized work through the appropriate procedure, retaining decisions and "
    "approvals already given in this conversation. Launch compute or change defaults, "
    "baselines or campaign direction only when authorized; a general check-in does not "
    "authorize those actions.\n\n"
    "After taking action, report what changed, what the evidence supports and what remains "
    "unresolved. Continue subsequent profiling work in this chat and stop at the session "
    "deliverable without scheduling background follow-up."
)


class CampaignError(ValueError):
    """The control-room ledger is invalid or incomplete."""


def load(root: Path = ORGAN_ROOT) -> dict:
    root = Path(root)
    path = root / "campaigns.yaml"
    if not path.is_file():
        raise CampaignError(f"{path}: missing campaign ledger")
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise CampaignError(str(exc)) from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise CampaignError("campaign ledger must have version 1")
    for kind in ("campaigns", "tasks"):
        rows = data.get(kind)
        if not isinstance(rows, list):
            raise CampaignError(f"{kind} must be a list")
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                raise CampaignError(f"{kind}: expected a mapping")
            for field in ("id", "title", "status", "updated", "next"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    raise CampaignError(f"{kind}: missing text {field}")
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", row["id"]) or row["id"] in seen:
                raise CampaignError(f"{kind}: invalid/duplicate id {row['id']}")
            seen.add(row["id"])
            if row["status"] not in STATUSES:
                raise CampaignError(f"{row['id']}: unknown status")
            for field in ("evidence", "issue"):
                if field in row and (
                    not isinstance(row[field], str)
                    or urlparse(row[field]).scheme != "https"
                    or not urlparse(row[field]).netloc
                ):
                    raise CampaignError(f"{row['id']}: {field} must be an HTTPS URL")
    ids = {c["id"] for c in data["campaigns"]}
    for task in data["tasks"]:
        if task.get("campaign") not in ids:
            raise CampaignError(f"{task['id']}: unknown campaign")
        relative = task.get("path", "")
        if not isinstance(relative, str):
            raise CampaignError(f"{task['id']}: task path must be text")
        path = root / relative
        if (
            not isinstance(relative, str)
            or not relative.startswith("tasks/")
            or not path.resolve().is_relative_to((root / "tasks").resolve())
            or not path.is_file()
        ):
            raise CampaignError(f"{task['id']}: missing or unsafe task path")
    return data


def marker(data: dict) -> str:
    digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return f"<!-- pulse-campaigns:{digest} -->"


def _md(value) -> str:
    return html.escape(str(value)).replace("|", "\\|").replace("\n", " ")


FIX_PROMPT = """Use the bug and profiling skills to investigate profiling problems systematically. Read PyAutoPulse/AGENTS.md, CHECKIN.md, campaigns.yaml and the relevant project evidence. Identify one concrete symptom, distinguish correctness from performance and measurement quality, and trace it to the exact setup, software and hardware. Preserve original evidence and unknowns; never call unreviewed timings a regression or accepted baseline. Propose a bounded plan and route any code changes through start-dev. Do not launch compute, change defaults or baselines, release or merge without the corresponding authorization."""


def markdown(data: dict) -> str:
    rows = [
        marker(data),
        "## Profiling Check In",
        "",
        "<details><summary>Full check-in prompt</summary>",
        "",
        "```text",
        PROMPT,
        "```",
        "",
        "</details>",
        "",
        f"Last check-in: {data.get('last_checkin') or 'not recorded yet'} (review date, not measurement freshness).",
        "",
        "## Active campaigns",
        "",
    ]
    for c in data["campaigns"]:
        if c["status"] in CLOSED:
            continue
        rows += [
            f"<details><summary>{_md(c['title'])} — {c['status']}</summary>",
            "",
            f"Reviewed {c['updated']}. {_md(c['next'])}",
            "",
        ]
        if c.get("evidence"):
            rows.append(f"[Campaign evidence]({c['evidence']})")
        rows += ["", "### Active tasks", ""]
        for task in data["tasks"]:
            if task["campaign"] == c["id"] and task["status"] not in CLOSED:
                rows.append(
                    f"- [{_md(task['title'])}]({URL}{task['path']}) — {task['status']}: {_md(task['next'])}"
                )
        rows += ["", "</details>", ""]
    rows += [
        "## Profiling evidence",
        "",
        "Choose a project, dataset and model on the interactive board.",
        "",
    ]
    return "\n".join(rows)


def render_html(data: dict, work_links=(), refreshed_at=None) -> str:
    def e(value):
        return html.escape(str(value), quote=True)

    def action(key, title, prompt, review=""):
        return (
            f'<div class="prompt-action"><button type="button" class="prompt-copy text" data-field="{key}-prompt">{e(title)}</button>{review}'
            f'<details id="{key}-details"><summary>Full prompt</summary><label for="{key}-prompt">Edit before copying</label>'
            f'<textarea id="{key}-prompt" rows="7">{e(prompt)}</textarea></details></div>'
        )

    reviewed = str(data.get("last_checkin") or "not recorded yet")
    review = f'<span class="review-meta" title="Ledger dates are review dates, not measurement freshness.">Last check-in: {e(reviewed[:10] if data.get("last_checkin") else reviewed)} · review date</span>'
    parts = [
        marker(data),
        theme().orchestration_panel(
            "pulse",
            "",
            "",
            PROMPT,
            work_links=work_links,
            copy_label="Profiling Check In",
            organ="pulse",
            refreshed_at=refreshed_at,
            refresh_url="https://github.com/PyAutoLabs/PyAutoPulse/actions/workflows/dashboard_refresh.yml",
        ),
        '<section class="controls" aria-label="Profiling actions">',
        action("fix", "Fix Profiling Systematically", FIX_PROMPT),
        review,
        '<span id="copy-status" role="status" aria-live="polite"></span></section>',
        '<h2 id="campaigns">Active campaigns</h2><div class="campaign-table"><table><thead><tr><th>Campaign</th><th>Status</th><th>Links</th></tr></thead><tbody>',
    ]
    for c in data["campaigns"]:
        if c["status"] in CLOSED:
            continue
        tasks = [t for t in data["tasks"] if t["campaign"] == c["id"] and t["status"] not in CLOSED]
        details_id = "campaign-" + c["id"]
        parts.append(
            f'<tr><td><strong>{e(c["title"])}</strong><details id="{details_id}" class="campaign-detail"><summary>{len(tasks)} {"task" if len(tasks) == 1 else "tasks"} · next step</summary><p>{e(c["next"])}</p><span class="review-meta">Reviewed {e(c["updated"])}</span><h3>Active tasks</h3>'
        )
        if not tasks:
            parts.append('<p class="muted">No open tasks.</p>')
        for t in tasks:
            issue = (
                f'<a class="icon-link" href="{e(t["issue"])}" aria-label="Issue for {e(t["title"])}" title="Issue">↗</a>'
                if t.get("issue")
                else ""
            )
            parts.append(
                f'<article class="campaign-task"><h4><a href="{URL}{e(t["path"])}">{e(t["title"])}</a>{issue}</h4><p class="review-meta">{e(t["status"])} · {e(t.get("priority", "normal"))}</p><p>{e(t["next"])}</p></article>'
            )
        parts.append(
            f'</details></td><td><span class="pill">{e(c["status"])}</span></td><td><div class="link-icons">'
        )
        if c.get("evidence"):
            parts.append(
                f'<a class="icon-link" href="{e(c["evidence"])}" aria-label="Evidence for {e(c["title"])}" title="Campaign evidence">↗</a>'
            )
        parts.append(
            f'<a class="icon-link" href="#{details_id}" data-open="{details_id}" aria-label="Tasks for {e(c["title"])}" title="Open tasks">☷</a></div></td></tr>'
        )
    parts += [
        '</tbody></table></div><p class="review-meta">Open means tracked, not necessarily running. <a href="'
        + URL
        + 'campaigns.yaml">Full ledger ↗</a></p>',
        '<h2 id="evidence">Profiling evidence</h2><p class="muted">Choose a project, dataset and model. Qualification belongs to each recorded setup.</p>',
    ]
    return "".join(parts)
