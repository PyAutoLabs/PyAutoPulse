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


def markdown(data: dict) -> str:
    rows = [
        marker(data),
        "## Check in on all profiling work",
        "",
        "Copy this into one chat. Add a campaign focus or idea before or after it, or leave it unchanged.",
        "",
        "```text",
        PROMPT,
        "```",
        "",
        f"Last check-in: {data.get('last_checkin') or 'not recorded yet'}. Ledger dates are review dates, not measurement freshness.",
        "",
        "## Active campaigns",
        "",
        "| Campaign | Status | Open tasks | Next step | Reviewed |",
        "|---|---|---:|---|---|",
    ]
    for c in data["campaigns"]:
        if c["status"] in CLOSED:
            continue
        n = sum(t["campaign"] == c["id"] and t["status"] not in CLOSED for t in data["tasks"])
        title = f"[{_md(c['title'])}]({c['evidence']})" if c.get("evidence") else _md(c["title"])
        rows.append(f"| {title} | {c['status']} | {n} | {_md(c['next'])} | {c['updated']} |")
    rows += [
        "",
        "## Active tasks",
        "",
        "Open means tracked, not necessarily running. Blockers and decisions still apply.",
        "",
        "| Task | Campaign | Status | Priority | Next step |",
        "|---|---|---|---|---|",
    ]
    for t in data["tasks"]:
        if t["status"] not in CLOSED:
            rows.append(
                f"| [{_md(t['title'])}]({URL}{t['path']}) | {t['campaign']} | {t['status']} | {_md(t.get('priority', 'normal'))} | {_md(t['next'])} |"
            )
    rows += [
        "",
        "Completed and superseded tasks remain in the [ledger](" + URL + "campaigns.yaml).",
        "",
        "## Profiling evidence",
        "",
    ]
    return "\n".join(rows)


def render_html(data: dict) -> str:
    def e(value):
        return html.escape(str(value), quote=True)

    campaigns = []
    for c in data["campaigns"]:
        if c["status"] in CLOSED:
            continue
        n = sum(t["campaign"] == c["id"] and t["status"] not in CLOSED for t in data["tasks"])
        title = (
            f'<a href="{e(c["evidence"])}">{e(c["title"])}</a>'
            if c.get("evidence")
            else e(c["title"])
        )
        campaigns.append(
            f"<tr><td>{title}</td><td>{e(c['status'])}</td><td>{n}</td><td>{e(c['next'])}</td><td>{e(c['updated'])}</td></tr>"
        )
    tasks = []
    for t in data["tasks"]:
        if t["status"] in CLOSED:
            continue
        issue = f' · <a href="{e(t["issue"])}">issue</a>' if t.get("issue") else ""
        tasks.append(
            f'<tr><td><a href="{URL}{e(t["path"])}">{e(t["title"])}</a>{issue}</td><td>{e(t["campaign"])}</td><td>{e(t["status"])}</td><td>{e(t.get("priority", "normal"))}</td><td>{e(t["next"])}</td></tr>'
        )

    def table(headers, rows):
        return (
            '<div class="tablewrap"><table><thead><tr>'
            + "".join(f"<th>{h}</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )

    return (
        marker(data) + '<section class="checkin"><h2>Check in on all profiling work</h2>'
        "<p>One prompt, one ongoing chat. Add a campaign focus or idea here, or tell the chat before or afterwards.</p>"
        f'<label for="checkin-prompt">Your check-in prompt</label><textarea id="checkin-prompt" rows="8">{e(PROMPT)}</textarea>'
        '<button type="button" id="copy-checkin">Copy check-in prompt</button><span id="copy-status" role="status" aria-live="polite"></span>'
        f'<p class="muted">Last check-in: {e(data.get("last_checkin") or "not recorded yet")}. Ledger dates are review dates, not measurement freshness.</p></section>'
        '<h2 id="campaigns">Active campaigns</h2>'
        + table(["Campaign", "Status", "Open tasks", "Next step", "Reviewed"], campaigns)
        + '<h2 id="tasks">Active tasks</h2><p>Open means tracked, not necessarily running. Blockers and decisions still apply.</p>'
        + table(["Task", "Campaign", "Status", "Priority", "Next step"], tasks)
        + f'<p>Completed and superseded tasks remain in the <a href="{URL}campaigns.yaml">ledger</a>.</p><h2 id="evidence">Profiling evidence</h2>'
    )
