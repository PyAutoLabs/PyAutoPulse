Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/bug/autolens_profiling/timing_noise_audit.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [autolens_profiling#362](https://github.com/PyAutoLabs/autolens_profiling/issues/362) is open, 0 comments, unassigned, last updated 2026-10-02 (filed from PR #361).
- Adjacent but distinct: PyAutoHeart#276 / PR #277 (unit-timing distinct baseline) completed 2026-10-04; that is Heart unit-test timing, not profiling gates.
- Next: start the audit (read-and-classify) phase via start_dev, reusing #362.

## Check-in 2026-10-07

- https://github.com/PyAutoLabs/autolens_profiling/issues/362 still open, 0 comments, unassigned, unchanged since 2026-10-02.
- Related new Mind draft: `draft/bug/autolens_profiling/call_accounting_ci_timing_threshold.md` (2026-10-06).


## Execution 2026-10-08 — phase 1 started

- Human direction (Pulse check-in, after the linear-solver programme closed): "move on to the next Pulse task"; phase 1 plan approved in chat. Issue #362 reused (plan comment posted 2026-10-08); Mind `active/timing_noise_audit_phase1_inventory.md` (a6e8aa1a); worktree `timing-noise-audit-p1-inventory`, branch `feature/timing-noise-audit-p1-inventory`; Opus executes.
- Scope: inventory of every timing assertion and production gate with estimator, samples, warm-up, pairing, clock, host qualification, cutoff, noise model, FP/FN risk and owner; PASS/FAIL/INCONCLUSIVE semantics; ranked fix phases with synthetic witnesses; read-only lister with `--check`. No gate or tolerance changes.


### Phase 1 shipped 2026-10-08

- [autolens_profiling#402](https://github.com/PyAutoLabs/autolens_profiling/pull/402) merged 2026-10-08 (lint green after main was un-reddened by #403, a PyAutoBrain theme drift). Mind record `complete/2026/10/timing-noise-audit-p1-inventory.md`. Issue #362 stays open for the fix phases.
- Inventory `results/notes/timing_noise_audit_2026_10.md`: 31 rows, 11 SOUND / 10 FRAGILE / 10 UNSAFE-SILENT. UNSAFE-SILENT includes dashboard `qualify()` (laptop rows with provenance, rows without load average and HPC rows without a host all qualify) — **Pulse-relevant**: `pulse/catalogue.py` accepts evidence on that flag, so today's "qualified" counts on the board are not a measurement-quality statement. The #361 trigger test is FRAGILE (near-zero power; INCONCLUSIVE silent under `pytest -q`; passed at a ratio of 0.79).
- Lister `scripts/misc/tooling/list_timing_assertions.py --check` is in lint.yml; campaign page `wiki/campaigns/measurement_tools.md` created.
- Proposed fix phases: (1) shared overhead verdict (test + cell, interval vs excess over budget, visible INCONCLUSIVE); (2) dashboard qualification + drift wording (contract change → Pulse coordination); (3) INCONCLUSIVE for go / lever rules, tie sets instead of argmax. Next: file phase 2 = fix (1) from this task, reusing #362; retire the subsumed Mind draft `call_accounting_ci_timing_threshold.md` when it is filed.


### Phase 2 started 2026-10-08

- Human: "do the next step" → fix phase (1) of the audit note, plan approved in chat; issue #362 reused (plan comment posted); Mind `active/timing_noise_audit_phase2_overhead_verdict.md` (3a3d4fc6); worktree `timing-noise-audit-p2-overhead-verdict`; Opus executes. The superseded Mind draft `call_accounting_ci_timing_threshold.md` ("increase it a bit so merge goes through") was retired on the human's approval — the guard is fixed, not relaxed.
- Scope: one `abba_overhead_verdict` used by both the CI test and `fixed_light_numba.py`; budget 12 ms of excess over the clean call; one-sided small-sample t-interval of the excess vs budget → PASS / FAIL / FAIL_GROSS / INCONCLUSIVE; n < 3 and below-1 ratios INCONCLUSIVE; cell raises only on FAIL/FAIL_GROSS and keeps the JSON otherwise; promotion requires PASS; the test warns visibly on INCONCLUSIVE; the 1.031 ratio constant goes. No budget raised.

---

# Audit timing tests and profiling gates for measurement noise

Issue: https://github.com/PyAutoLabs/autolens_profiling/issues/362
Issued: 2026-10-02
Type: bug
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: large
Autonomy: supervised
Priority: high
Status: planned
Consequence: judge
Review-minutes: 25
Unattended: ready

# Audit timing tests and profiling gates for measurement noise

Type: bug
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: large
Autonomy: supervised
Priority: high
Consequence: judge

## Goal
Audit all runtime-sensitive tests and the production profiling acceptance mechanisms for correct treatment of measurement noise. Inventory absolute/relative cutoffs, warmup, repeated blocks, pairing/order, sample count, clock/synchronization, host qualification, estimator uncertainty and multiple comparisons. Follow dependencies into other repos only when the inventory identifies them; split implementation into bounded phases after the audit.

## Trigger and evidence
PR autolens_profiling#361 failed test_call_accounting_covers_a_real_likelihood_call at ratio 1.031073665 against 1.031; blocks [1.0218478812434695, 1.0243047139025747, 1.0470684004725312]. Equality and coverage (99.95%) passed. The guard compares block range to the entire overhead budget, not uncertainty relative to the excess. Five local repeats were all too noisy to assert the strict cutoff. The local stack differs from CI, so they demonstrate scatter, not proof of compliance. CI log: Actions run 36985476995, job 110769406158.

## Acceptance
- Produce an inventory of timing assertions and production gates, each with a noise model, assumptions, false-positive risks and ownership.
- Define PASS / FAIL / INCONCLUSIVE semantics: inconclusive must not silently qualify a profiling result or be reported as a measured pass.
- Preserve correctness gates, gross-regression protection, declared practical budgets and pre-registered campaign decisions; do not merely increase tolerances or retry until green.
- Account for small samples, non-normal/outlier timings, dependence/drift and multiple comparisons; state limits of confidence-bound methods.
- Add deterministic synthetic-data tests for clear gains/regressions, boundaries, noisy/insufficient observations, invalid timings and severe regressions, plus controlled repeated execution where needed.
- Reconcile test helpers and production instruments so their interpretation cannot drift. Separate cheap correctness CI from hardware-dependent performance claims where appropriate.

## Original user request
fix the noise cutoff, intake na issue to fix this long term (e.g. check all trests but also make sure the whole mechanism accounts ofr noise) and then prm and continue this task

<!-- formalised by the Intake (Conception) Agent on 2026-10-02 from file:tmp/noise-audit.md -->
