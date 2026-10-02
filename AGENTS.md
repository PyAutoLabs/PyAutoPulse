# PyAutoPulse — agent instructions

This file is for AI coding agents (Claude Code, Codex, Cursor, etc.) and humans
discovering this repository. PyAutoPulse is the **Pulse** organ of the PyAuto
organism — where the organism feels how fast it runs. It is the cross-project
profiling dashboard over the `<lib>_profiling` project repos (today
`autolens_profiling`): it will own the profiling instance registry, the
versioned `profiling-summary` read contract, the ingest receipts (resolved
commit per project per render) and the Pages board. It validates the exchange
contract only and never judges a timing — the Brain's profiling conductor
(`triage`) does. The project repos keep their producers, results, drift policy
and their own Pages page. This repo is a stub: the registry, reader, board and
workflows arrive in phase 2 of the `profiling-organ-birth` epic. Design:
`PyAutoBrain/docs/research/profiling_inference_organs.md`.

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
