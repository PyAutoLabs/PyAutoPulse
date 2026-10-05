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
PROMPT = """Use PyAutoPulse as the home for all profiling work in this chat. Read PyAutoPulse/AGENTS.md and CHECKIN.md, then campaigns.yaml, the linked tasks and current project campaign ledgers. Check every open campaign and task for updates since the last check-in: results, jobs, PRs, releases, blockers and the next bounded step. Distinguish verified updates from stale or unavailable evidence; do not infer success from missing data. Give me one concise campaign-by-campaign summary and a proposed priority order. Apply any campaign direction or ideas I supply before or after this prompt; otherwise cover everything. Keep the overall check-in even when I focus one campaign. Update the Pulse ledger with verified facts and dated source links, regenerate the board, and use the repository workflow to persist changes. Use Brain's profiling conductor for scientific judgement and project drivers for execution. Do not launch new compute, change defaults or baselines, or bypass a human/release gate merely to check in. Continue managing subsequent profiling requests in this chat. Optional direction: [leave blank, name a campaign, or suggest an idea]."""


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


def render_html(data: dict) -> str:
    def e(value):
        return html.escape(str(value), quote=True)

    def action(key, title, prompt, review=""):
        return (
            f'<div class="prompt-action"><button type="button" class="copy text" data-field="{key}-prompt">{e(title)}</button>{review}'
            f'<details id="{key}-details"><summary>Full prompt</summary><label for="{key}-prompt">Edit before copying</label>'
            f'<textarea id="{key}-prompt" rows="7">{e(prompt)}</textarea></details></div>'
        )

    reviewed = str(data.get("last_checkin") or "not recorded yet")
    review = f'<span class="review-meta" title="Ledger dates are review dates, not measurement freshness.">Last check-in: {e(reviewed[:10] if data.get("last_checkin") else reviewed)} · review date</span>'
    parts = [
        marker(data),
        '<section class="controls" aria-label="Profiling actions">',
        action("fix", "Fix Profiling Systematically", FIX_PROMPT),
        action("checkin", "Profiling Check In", PROMPT, review),
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
