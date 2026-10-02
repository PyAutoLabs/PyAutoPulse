# PyAutoPulse — agent instructions

This file is for AI coding agents (Claude Code, Codex, Cursor, etc.) and humans
discovering this repository. PyAutoPulse is the **Pulse** organ of the PyAuto
organism — where the organism feels how fast it runs. It is the cross-project
profiling dashboard over the `<lib>_profiling` project repos (today
`autolens_profiling`): it owns the profiling instance registry, the versioned
`profiling-summary` read contract, the ingest receipts (resolved commit per
project per render) and the Pages board. It validates the exchange contract
only and never judges a timing — the Brain's profiling conductor (`triage`)
does. The project repos keep their producers, results, drift policy and their
own Pages page. Design: `PyAutoBrain/docs/research/profiling_inference_organs.md`;
the contract as read and every file format: `REFERENCE.md`.

<!-- repos_sync:map:begin -->
**You are one organ of the PyAuto organism** — an agentic ecosystem for
human-led, natural-language software development. The organs below are
peer repositories; this repo is one of them, not a part of another.
Canonical boundaries live in `PyAutoBrain/ORGANISM.md`; the full body map
(every repo, not just organs) is `PyAutoMind/repos.yaml`.

| Organ | Repo | Role |
|-------|------|------|
| **Brain** | PyAutoBrain | Reasoning/orchestration layer; how work is decomposed and routed; the specialist agents. |
| **Mind** | PyAutoMind | Intent, goals, priorities, workflow state; every task starts as a markdown prompt here. |
| **Cortex** | PyAutoCortex | The Cortex — where the organism keeps track of what is true: the science body map (`projects.yaml`) and one ledger per science project (what was run, what came back, what was learned, where to pick up); the science mirror of the Mind (runs and a dated log, not prompts and PRs). |
| **Memory** | PyAutoMemory | Long-term scientific/software/project knowledge (see science pointer below). |
| **Eyes** | PyAutoEyes | The Eyes — where the organism sees what its figures look like: the cross-project visualization dashboard over the `<lib>_visualization` project repos (autolens_visualization, autogalaxy_visualization, autofit_visualization and autocti_visualization) — the registry of those repos, the tracked-manifest read contract (`gallery/viz_manifest.yaml`) and the Pages board that links to their PNGs as the single point of contact for the visual behaviour of the whole ecosystem. Renders nothing and copies no figures (the project repos render and hold them); never judges them (the Brain's Eyes conductor does) and never edits library plot code (critiques route through intake). |
| **Heart** | PyAutoHeart | Health/readiness — the authoritative "is it safe to release?" verdict. |
| **Hands** | PyAutoHands | Packaging, tagging, notebook generation, PyPI release execution. |
| **Pulse** | PyAutoPulse | The Pulse — where the organism feels how fast it runs: the cross-project profiling dashboard over the `<lib>_profiling` project repos (today autolens_profiling) — the instance registry, the versioned `profiling-summary` read contract (v1 live at `autolens_profiling/dashboard/summary.json`), the ingest receipts (resolved commit per project per render) and the Pages board. Validates the exchange contract only; never moves pins, combines unmatched timings, applies the compile threshold to runtime, computes an ecosystem-wide speed score or issues a Heart verdict, and never judges (the Brain's profiling conductor does); the project repos keep their producers, results, drift policy and their own Pages page. |
| **Nerves** | PyAutoNerves | The Nerves — the configuration/serialization layer connecting workspace conventions to libraries (layered config, version handshake, test_mode), delivered as the `autonerves` package. |
| **Gut** | PyAutoGut | Owns the lifecycle of condemned self-material (stale branches, stashes, dead code/tests): holds it as durable, recoverable git refs through a transit window and voids it on a sweep. The storage mirror of Memory (retention vs release). |

Call chain (always this order): **Brain → Heart (gate) → Build (execute)**. Brain agents are **conductors** (front-door; a human drives them; they decide *and* act) or **faculties** (read-only opinions the conductors consult; they judge and stop). New capability grows as a faculty, not a new organ, unless it owns state or effects no existing organ can.

Generated from `PyAutoMind/repos.yaml` + `PyAutoBrain/ORGANISM.md`; edit there, then run `python3 PyAutoMind/scripts/repos_sync.py --write`.
<!-- repos_sync:map:end -->

<!-- repos_sync:history:begin -->
## Never rewrite history

Never rewrite pushed history on any repo with a remote — no `git init` over a
tracked repo, no force-push to `main`, no fresh-start "Initial commit", no
`filter-repo` / `filter-branch` / `rebase -i` on pushed branches. To get a
clean tree: `git fetch origin && git reset --hard origin/main && git clean -fd`.
<!-- repos_sync:history:end -->

<!-- repos_sync:deliverable:begin -->
## Sessions end at their deliverable

A session ends when it reports its deliverable — never arm anything that
outlives the turn to wait for CI, a review or a merge: no `send_later`, no
`subscribe_pr_activity`, no `CronCreate`, no `ScheduleWakeup`, no `/loop`, no
`RemoteTrigger` create/update/run. Judge once, report, stop; the human re-runs
`/prm` (or the batch review) when it is green. Measured: five batch members
armed hourly check-ins on 2026-08-31, and a mobile `/prm` re-armed a 60-minute
`send_later` hourly all night on 2026-09-03 with no task active, draining usage.
<!-- repos_sync:deliverable:end -->

<!-- repos_sync:filing:begin -->
## Where to file

Questions, help with code or an analysis, ideas, bug reports and results from a
user or collaborator — or an agent acting for one — go to
<https://github.com/orgs/PyAutoLabs/discussions> in the matching category
(Help & Questions, Ideas & Proposals, Bugs & Errors, Show and tell;
Announcements is maintainers-only), never to this repo's Issues. An agent never
runs `gh issue create` for such a report: it drafts the title, category and
body and hands them to the human (sessions cannot create Discussions). Only the
development flow — Mind prompt → `/start_dev` → `/create_issue` → one issue per
task → PR — opens issues here. Why: `PyAutoMind/policy/community_surface.md`.
<!-- repos_sync:filing:end -->

## What this repo is

The design has **two layers** (`profiling_inference_organs.md`, PyAutoBrain#444):

- **Project repos** `<lib>_profiling` run the producers, keep the result JSONs,
  own the drift policy and the meaning of every number, render their own Pages
  page, and publish one **summary** file behind the `profiling-summary`
  contract. Registered today: `lens` → `autolens_profiling`
  (`dashboard/summary.json`, contract documented in that repo's
  `dashboard/README.md`).
- **This organ** reads each registered summary at one resolved commit,
  validates the exchange contract, records a receipt, and publishes the
  cross-project board (`dashboard.md` + `dashboard.html` on Pages, with
  `state.json` for the Brain cockpit and `badge.json`).

## What this organ owns (its growth-rule state)

| State | File | Written by |
|---|---|---|
| Instance registry | `registry.yaml` | a human, through the dev flow |
| The read contract as this organ implements it | `pulse/summary.py` + `REFERENCE.md` | the dev flow (reader first, producer second on a version bump) |
| Ingest receipts — the resolved commit, fetch time, outcome and errors per instance | `receipts/<instance>.json` | `bin/pyauto-pulse board` / `fetch` / `check` |
| Last-good snapshots — the summary as captured, with its commit and fetch time | `snapshots/<instance>.json` | the same, on a good read only |
| The board | `dashboard.md`, `dashboard.html`, `state.json`, `badge.json` | `bin/pyauto-pulse board` (and `dashboard_refresh.yml`) |

Repository location and GitHub identity are **not** owned here: a registry row
names its project by its PyAutoMind body-map identity (`repo`), and `path` /
`github` are read from `PyAutoMind/repos.yaml` at run time (`--mind PATH`,
else `$PYAUTO_MIND`, else `$PYAUTO_ROOT/organs/PyAutoMind` or
`$PYAUTO_ROOT/PyAutoMind`, else beside this organ). There is no second
catalogue of repositories.

## Boundary (what this organ never does)

From the spec's "Profiling domain contract", verbatim:

> A memory value cannot enter a seconds series, and a component timing cannot be
> presented as a full likelihood cost.

> The organ displays project-supplied drift candidates and provenance. It does not
> move pins, combine unmatched timings, apply the compile threshold to runtime,
> compute an ecosystem-wide speed score or issue a Heart verdict. A drift item links
> to its pair of records and offers the existing profiling triage door. A confirmed
> library defect subsequently takes the normal Mind development route.

In practice:

- **Recomputes no ratio.** The board prints the producer's own `comparisons[]`
  ratio and status verbatim; it never divides two measurements.
- **Never combines unmatched records.** A comparison whose two records differ in
  axis, or in hardware identity (`device`, `backend`, `precision`, `host`), is
  listed as *refused by the reader* with its reason and no ratio; accepted
  pairs are grouped by hardware so changed hardware is always a separate group.
- **Ranks nothing across projects** — no league table, no speed score.
- **Issues no verdict.** `state.json` summarises this organ's monitoring scope
  only, never release readiness (that is the Heart's).
- **Judges nothing.** The Brain's profiling conductor is the only judge: a
  drift item's only handoff is the manual `/profiling triage <comparison_key>`
  prompt (`kind: prompt`, `safety: scientific_judgement`). Fetching or
  rendering never submits a job, re-pins a baseline, logs a lesson, edits
  source or grants approval.
- **Imports no scientific library.** The reader is PyYAML + stdlib.

## Three notions, kept apart

Every row and every detail section keeps three separate labels:

1. **Integrity** — transport and schema: `ok`, `invalid`, `unavailable`,
   `unsupported`, or `cached` (the latest fetch failed and the last good
   capture is shown with its *original* evidence and fetch times plus the new
   error; no render ever re-ages it).
2. **Freshness** — against the producer's own `valid_until`. When the producer
   declares none, the board says "freshness policy unspecified" with the
   evidence's age; it never invents a TTL.
3. **Qualification** — the producer's own `qualified` flags, counted. Unknown
   provenance is shown unqualified, never dropped; healthy transport never
   makes unknown quality green. A valid empty feed reads "no measurements",
   never "all measurements passed".

## Adding an instance

1. The project repo publishes a summary behind a contract version this reader
   supports, documented in that repo.
2. Add a validated fixture under `tests/fixtures/` showing its conventions read
   through the same code path (no project-specific branching — see
   `second_producer.json`).
3. Add one `registry.yaml` row (`instance`, `repo` = body-map identity,
   `summary_path`, `supported_schema`, `dashboard_url`, `library_refs`,
   `cortex_project`). One summary is registered once; discovery by a
   `*_profiling` name alone is insufficient.
4. `bin/pyauto-pulse board` and commit the board, receipt and snapshot.

## Commands

```bash
bin/pyauto-pulse check            # registry + body map, ingest at one commit, receipt, dashboard current, state.json → "check: OK"
bin/pyauto-pulse check --offline  # the same over the committed receipts + snapshots (CI)
bin/pyauto-pulse board            # ingest, then render dashboard.md/.html, badge.json, state.json
bin/pyauto-pulse census           # one line per instance from the committed snapshots
bin/pyauto-pulse fetch [--instance K]  # ingest + receipt only
```

Before a PR: `ruff check . && ruff format --check . && pytest -q tests && bin/pyauto-pulse check --offline`.
