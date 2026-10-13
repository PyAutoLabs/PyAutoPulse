Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/feature/autolens_profiling/gradient_cost_probe.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [autolens_workspace_developer#117](https://github.com/PyAutoLabs/autolens_workspace_developer/issues/117) closed 2026-07-28; no change since the pin. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Next: select one bounded step when prioritised.

## Check-in 2026-10-07

- Context: Heart unit-test timing (PyAutoLens py3.13, 2026-10-07) flagged test__forward_gradient_matches_reverse_through_fitness 5.03→12.60 s and test__multi_start_gradient_point_source_fit_runs_in_forward_mode 15.51→30.38 s. https://github.com/PyAutoLabs/PyAutoLens/pull/768 rewrote that test file, so this is not a controlled library-cost comparison; this probe is the right instrument. Unissued.


## Check-in 2026-10-13

- Campaign review: #408/#409 merged 2026-10-09. #410 -> #411 -> #412 remain OPEN, lint SUCCESS at reviewed heads ffddf755/a5de4d49/9ce9a132; Mind claims all three awaiting merge. Review flagged statistical/estimator decisions, then human /prm in order. Issue #362 stays open. No new measurement JSON; v2 catalogue remains 0 qualified / 112 records, 0 comparisons.
- Task next step: Unissued. New context 2026-10-07: Heart unit-test timing flagged PyAutoLens forward-gradient tests +150%/+96% after PyAutoLens#768 rewrote that test file; not a controlled comparison, and this probe is the right instrument. Select one bounded step when prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.

---

# A gradient-cost probe: forward vs `value_and_grad` ms/eval and a strict FD check, on any registry cell

Type: feature
Target: autolens_profiling
Repos:
- autolens_profiling
Themes:
- jax-gradient
- profiling
Difficulty: small
Autonomy: safe
Priority: low
Status: draft
Consequence: glance
Witness: the probe runs on CPU and prints a forward/grad ms-per-eval table and an FD table for a named cell
Review-minutes: 3
Unattended: ready
Filed: 2026-09-04

Build a standing profiling tool that answers, for any profiling cell, **what a gradient
evaluation costs and whether it is correct**. Split out of
`draft/feature/autolens_profiling/gradient_slam_mass_pix_target.md` on 2026-09-04 by human
decision: the `gradient-slam-baseline` epic asks whether gradients reduce the *number* of
inference steps, not what a gradient costs, so the probe is not a science phase and gates
nothing. It is a tool — keep it in mind, and run it whenever someone wants the number.

## Why

The only rectangular kernel-CDF gradient cost datum that exists anywhere is a **CPU** one:
the ~17× `value_and_grad`-over-forward anomaly recorded in
autolens_workspace_developer#117 and `searches_minimal/pix_prodigy_findings.md`. It has
**never been re-measured on an A100**, so nobody knows whether it is a real cost of the
mesh likelihood or an artifact of the CPU path. That is a question worth being able to
answer on demand, on any cell, rather than a question worth a science phase — hence a
script and a submit script, not a programme.

## What to build

### 1. The probe — `scripts/misc/searches/probe_gradient_cost.py`

A CLI tool taking `--cell <model_type>` — **default `mass_pix`**, and accepting **any cell
registered in `scripts/misc/searches/_targets.py`**, so it is not tied to one target. For
the named cell it reports:

- the **forward** likelihood cost in ms/eval;
- the **`value_and_grad`** cost in ms/eval;
- **their ratio** — the number the 17× anomaly is about;
- the **jit compile time** for each of the two;
- a **strict finite-difference check on every free parameter of the cell** — each
  FD/analytic pair agreeing to a declared tolerance, no parameter skipped, no NaN or
  non-finite entry in either gradient, reported as a per-parameter table.

Follow the FD-certification pattern of
`@autolens_workspace_test/scripts/imaging/jax_grad/pixelization.py` — that script is the
reference for how the check is set up and what it asserts.

The number of free parameters is the cell's own, read from the model rather than hardcoded,
so the FD table is complete for whatever cell is asked for.

### 2. The submit — `@autolens_profiling/hpc/batch_gpu/`

One submit script for **one A100 task** running the probe on the requested cell, with the
usual `WALL-BASIS` block. This is what turns "the 17× has never been measured on a GPU"
into a one-command answer.

## Out of scope

Anything in the `gradient-slam-baseline` ledger
(`@autolens_profiling/results/notes/gradient_slam/LEDGER.md`) — the `mass_pix` target
itself, its Nautilus and Prodigy drivers, their submits, and the Cortex phases 21–23 that
run them. This prompt adds a tool beside them and changes none of them. No library code in
PyAutoArray / PyAutoGalaxy / PyAutoLens: if the probe finds a real gradient-cost or
gradient-correctness fault, that is a bug filed in the Mind, not fixed here. No RAL
submission as part of the task — the submit script is written, not run.
