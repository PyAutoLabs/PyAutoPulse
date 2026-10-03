Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/bug/autolens_profiling/timing_noise_audit.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

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
