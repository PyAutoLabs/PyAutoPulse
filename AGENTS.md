# PyAutoPulse — agent instructions

## Profiling campaign front door

Read `CHECKIN.md` for all-campaign updates and one-chat operation. Pulse now owns
profiling campaign intent and pending tasks in `campaigns.yaml` and `tasks/`,
including prompts migrated from Mind (`migration.yaml`). The board displays
the editable check-in prompt, active campaigns, open tasks, then measurements.
Mind retains bounded development issue/PR lifecycle and repository claims;
project repos retain measurement evidence. This explicit ownership update takes
precedence over older descriptions of Pulse as only a summary reader.


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
**You are one peer organ of the PyAuto organism** (human-led, natural-language software development), not a part of another. Boundaries: `PyAutoBrain/ORGANISM.md`; every repo: `PyAutoMind/repos.yaml`.

| Organ | Repo | Role |
|-------|------|------|
| **Brain** | PyAutoBrain | Reasoning and orchestration: decomposes and routes work through its conductors and faculties. |
| **Broca** | PyAutoBroca | Assistant evaluation history, upkeep evidence and its dashboard. |
| **Mind** | PyAutoMind | Intent, priorities and workflow state; every task starts as a prompt here. |
| **Cortex** | PyAutoCortex | What is true in the science: the project body map and one ledger per project. |
| **Memory** | PyAutoMemory | Long-term scientific, software and project knowledge. |
| **Eyes** | PyAutoEyes | Cross-project figure dashboard over the `<lib>_visualization` repos. |
| **Ears** | PyAutoEars | Read-only community listening: conversation snapshots and coverage. |
| **Heart** | PyAutoHeart | Health/readiness — the authoritative release verdict. |
| **Hands** | PyAutoHands | Packaging, tagging, notebooks and PyPI release execution. |
| **Pulse** | PyAutoPulse | Cross-project profiling dashboard over the `<lib>_profiling` repos. |
| **Insight** | PyAutoInsight | Inference campaign intent, instance registry and evidence dashboard. |
| **DNA** | PyAutoDNA | Software-stack specifications, environment inventories and upgrade campaigns. |
| **Nerves** | PyAutoNerves | Configuration/serialization layer (`autonerves`): layered config, version handshake, test_mode. |
| **Gut** | PyAutoGut | Condemned branches, stashes and dead code, held as recoverable refs until swept. |

Call chain: **Brain → Heart (gate) → Build (execute)**. Conductors decide *and* act; faculties judge read-only and stop. New capability grows as a faculty, not an organ, unless it owns state or effects no organ can.

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
| Frozen snapshots — a producer's stamped baseline (`day_zero`), captured once at one commit with a manifest; never rewritten | `snapshots/<label>/<instance>.json` | `bin/pyauto-pulse freeze` (by a human-approved task); verified by `check` |
| The board | `dashboard.md`, `dashboard.html`, `state.json`, `badge.json` | `bin/pyauto-pulse board` (and `dashboard_refresh.yml`) |

Repository location and GitHub identity are **not** owned here: a registry row
names its project by its PyAutoMind body-map identity (`repo`), and `path` /
`github` are read from `PyAutoMind/repos.yaml` at run time (`--mind PATH`,
else `$PYAUTO_MIND`, else `$PYAUTO_ROOT/organs/PyAutoMind` or
`$PYAUTO_ROOT/PyAutoMind`, else beside this organ). There is no second
catalogue of repositories.

## Setup catalogue migration

The reader accepts `profiling-summary` v1 and v2; registry rows still pin one
exact version. V2 adds setup identities, typed evidence and explicit reference
selections (`pulse/catalogue.py`, `REFERENCE.md`). The live lens registry now reads the project v2 catalogue. Accepting a schema is not scientific
acceptance and does not launch a baseline campaign. The setup browser reads the captured index and verifies same-commit detail shards.

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
bin/pyauto-pulse freeze --instance lens --label day_zero --commit <sha>  # frozen baseline, once
bin/pyauto-pulse freeze --instance lens --label day_zero_gradient --measurement gradient --commit <sha>  # one measurement's stamps
bin/pyauto-pulse fetch [--instance K]  # ingest + receipt only
```

Before a PR: `ruff check . && ruff format --check . && pytest -q tests && bin/pyauto-pulse check --offline`.

<!-- repos_sync:standards:begin -->
## Shared standards

Before changing a shared interface, consult the applicable
[organism standard](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/standards.md)
on demand, identify affected consumers, and validate their adoption. Change
generated guidance at its canonical source and regenerate.

For board changes, follow the applicable sizing, navigation and orchestration
standards and reuse Brain’s shared components. Keep domain data, prompt meaning
and approval boundaries with the board’s owner.
<!-- repos_sync:standards:end -->
