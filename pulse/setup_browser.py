"""Render setup navigation from captured v2 evidence; never select scientific truth."""

from __future__ import annotations

import html
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import quote

from pulse import ORGAN_ROOT


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
        (ORGAN_ROOT / "pulse/setup_browser.js").read_text(),
    )


def render(snapshot):
    doc = snapshot.doc or {}
    if doc.get("version") != 2:
        return ""
    instance = snapshot.instance
    payload = {
        "catalogue": doc,
        "instance": instance.instance,
        "label": instance.repo.removesuffix("_profiling").replace("autolens", "AutoLens"),
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


def markdown(snapshot):
    doc = snapshot.doc or {}
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
