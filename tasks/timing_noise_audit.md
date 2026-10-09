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


### Phase 2 shipped 2026-10-08

- [autolens_profiling#404](https://github.com/PyAutoLabs/autolens_profiling/pull/404) merged 2026-10-08 (lint green after a catalogue/dashboard stamp refresh). Mind record `complete/2026/10/timing-noise-audit-p2-overhead-verdict.md`. Issue #362 stays open.
- Rule as built (`scripts/misc/likelihood_breakdown/overhead_verdict.py`): excess ms = (ratio − 1) × clean mean; one-sided 95 % t-bounds; invalid → ValueError; mean ratio > 1.5 → FAIL_GROSS; n < 3 → INCONCLUSIVE; upper bound < 0 → INCONCLUSIVE (host-noise signature); upper ≤ budget → PASS; lower > budget → FAIL; else INCONCLUSIVE. Cell raises only on FAIL/FAIL_GROSS; promotion requires PASS on both arms; CI INCONCLUSIVE is a visible warning; no budget raised.
- Exposed facts (no JSON rewritten): 6 of 17 published RAL rows, including the pinned 413 ms row ([−7.3, +19.4] ms), are INCONCLUSIVE on their own blocks rather than PASS.
- Human decision: on the ~15–17 ms CI fixture the shared 12 ms budget can only fail through the gross guard; the CI test is documented as the coverage + cached-site-count + gross-breakage guard, and the ms budget is judged on the 225–415 ms production rows.
- Next: fix phase (2) — `build_dashboard.qualify`/`drift` wording. This changes the `profiling-summary` contract Pulse ingests; plan it as a two-repo task (autolens_profiling producer + PyAutoPulse reader/fixtures) before any producer change lands.


## Execution 2026-10-08 — phase 3 (fix phase 2: dashboard qualification + drift wording)

- Human: "continue … --auto" after the plan was presented in the Pulse chat; issue #362 reused (plan comment https://github.com/PyAutoLabs/autolens_profiling/issues/362#issuecomment-6067418030). Mind `active/timing_noise_audit_phase3_qualify_drift.md` (f27988f1); branch `feature/timing-noise-audit-p3-qualify-drift`; Opus executes.
- **Correction to the phase 1/2 notes above:** Pulse's live `lens` registry reads `dashboard/catalogue.json` (`profiling-summary@2`) since 2026-10-05 (3c7bed2). That producer (`build_catalogue.py`) hard-codes `qualified: false` on every record, and its comparisons list is empty. `build_dashboard.qualify()`/`drift()` feed only the v1 `summary.json` (project dashboard and badge). The P6 gap therefore never reached Pulse live, and fix (2) is a single-repo change: no Pulse reader change was needed.
- Human decision 2026-10-08: `drifted` / `improved` keep their status and carry a "single-sample endpoint(s)" caveat; only the within-band case changes (`flat` only with repeat summaries on both endpoints, else `insufficient`).
- Heart readiness was YELLOW (8 organism-wide manifest-drift reasons + "no rehearsal for current source"); the human acknowledged that list for this PR on 2026-10-08.
- PR [autolens_profiling#405](https://github.com/PyAutoLabs/autolens_profiling/pull/405) opened 2026-10-08. Verified on the branch: 1169 passed / 6 skipped; independent review CLEAN; Pulse v1 `validate()` returns [] before and after. `summary.json` effect: 159 records, qualified 2 → 2 (no record changed), `flat` 4 → 0, `insufficient` 135 → 139, `improved` 6 → 6 with the caveat. Audit counts now 15 SOUND / 8 FRAGILE / 8 UNSAFE-SILENT.
- Carry-forward: when the v2 catalogue starts qualifying records (setup-baseline reference-host decision), it must reuse the producer's `is_reference_host_class` rule rather than a separate one.
- Next: /prm the PR (judge tier, human merge); then fix phase (3) — INCONCLUSIVE for go / lever rules, tie sets instead of argmax.


### Phases 3–5 merged 2026-10-08 (fix phases 2–4)

- [autolens_profiling#405](https://github.com/PyAutoLabs/autolens_profiling/pull/405) merged 19:46Z (f6e6982); Mind record `complete/2026/10/timing-noise-audit-p3-qualify-drift.md` (d774cbb1).
- [autolens_profiling#406](https://github.com/PyAutoLabs/autolens_profiling/pull/406) merged 20:19Z (94861700): shared `ab_verdict.py` (`ab_rule_verdict`, `tie_set`, `paired_block_ratio_interval`) wired into C6, C7, P2, C10. Re-judged committed rows: no go / no-go / NO_LEVER call changed; 7 of 9 committed C10 "best" picks are tie sets (IP-4a's 2.37x leader ties with four others; the human decision not to ship it stands). Flagged decision: C10 vmap rows measured for the tie set's `point_leader` only. Mind record f55f220e.
- [autolens_profiling#407](https://github.com/PyAutoLabs/autolens_profiling/pull/407) merged 20:43Z (8be806cc): shared `round_bootstrap.py` (paired whole-round resampling, `effective_n = n_rounds`) in seven cells. Witness: iid CI 0.14–0.39x as wide as the round CI; 40-seed coverage 0.85 vs 0.33 at nominal 0.90. RAL CPU / A100 calls unchanged; laptop C6 solved `rev_analytic` GO -> INCONCLUSIVE ([0.805, 0.854] vs 0.85). The review returned FINDINGS (label strings); the fix commit 63642d52 was re-reviewed by the main session before merge.
- Heart was YELLOW throughout with an organism-wide manifest-drift + no-rehearsal set; the human acknowledged that set for these PRs on 2026-10-08.
- #407 close-out: Mind record `complete/2026/10/timing-noise-audit-p5-round-bootstrap.md` (a9eb5864). Fix phases (5) and (6) NOT started at session end (no branch, Mind entry or plan comment); resume at start_dev with slug `timing-noise-audit-p6-median-headline-gpu-marker` from main 8be806c.
- Leftovers recorded in the audit note: phase 3b (C1/C3/C4/C5 have no interval), multiple-comparison policy (Holm/Bonferroni), `gpu_bottleneck_map` still per-call. Next: fix phase (5) P8/P9, then (6) P3/P5 (human authorized both under --auto 2026-10-08).

## Execution 2026-10-09 — fix phases (5)-(6) merged; phase 3b + leftovers to PR

- Human (Pulse chat 2026-10-09): "finish up the timing task", then "prm and then do 3b and leftovers fully wrap up --auto" and "do all work until complete --auto". Effective level supervised (bug, Consequence judge): every PR ends at PR-open for a human `/prm`. Plan: https://github.com/PyAutoLabs/autolens_profiling/issues/362#issuecomment-6079746240
- Heart: this morning's STALE/monitoring-RED set was human-acknowledged for these PRs. Later Heart went RED on `release validation FAILED (stage integrate)`; the human chose the development-only Heart-RED override for #412 (recorded https://github.com/PyAutoLabs/autolens_profiling/issues/362#issuecomment-6083878510).
- VERIFIED merged 2026-10-09 via human `/prm` (every CI job green): [#408](https://github.com/PyAutoLabs/autolens_profiling/pull/408) (3ce8d789) P8 median headline beside the block mean in 11 runtime cells, drift compares like estimators only; P9 timeouts INCONCLUSIVE unless qualified (all 4 committed markers are laptop/no-load; the ALMA laptop entry is now "did not finish (inconclusive)"). [#409](https://github.com/PyAutoLabs/autolens_profiling/pull/409) (4db4d988) P3 unsettled warm-up -> INCONCLUSIVE (0/28 committed unsettled); P5 witness PASS/FAIL only on the reference host class (all 8 committed laptop/untagged verdicts -> INCONCLUSIVE). Mind records `complete/2026/10/timing-noise-audit-p6-…`, `…-p7-…`.
- OPEN, stacked, merge in order (all reviewed CLEAN after fixes; no compute; no committed JSON rewritten):
  - [#410](https://github.com/PyAutoLabs/autolens_profiling/pull/410) phase 3b: C1/C3/C4/C5 on paired round-bootstrap intervals; Holm helper (`ab_verdict.holm_family_verdict`). Suite 1341/6. No decision changed (memo-policy NO_LEVER, scaling PASS, A100 no-lever stand); C1's 128 flags INCONCLUSIVE (4 < 5 repeats); 2 laptop logdet rows INCONCLUSIVE.
  - [#411](https://github.com/PyAutoLabs/autolens_profiling/pull/411) one family-wise policy (Holm, family = one verdict) for C6/C10/C11; C12 paired rounds (A100 MDI 5.45 % -> 0.94 %); P2 between-row drift. Suite 1376/6. C6 deciding GO routes unchanged; C10 tie sets widen (IP-4a 5 -> 7), no named best changed; numba-interferometer kill "passed" -> INCONCLUSIVE (4 rounds).
  - [#412](https://github.com/PyAutoLabs/autolens_profiling/pull/412) headline completion (README, breakdown/datacube/mge_mass cells), wall basis +50 s/invocation (A100 source_plane_solved submit 0:20 -> 0:27), `single_jit_repeats` support so `flat` is reachable. Suite 1405/6. Latent additive v2 metric `cube_single_jit_median`; no other profiling-summary@2 change.
- Audit end state (#412): 38 rows, 35 SOUND / 3 FRAGILE / 0 UNSAFE-SILENT.
- Open human decisions (none blocks merge): C1 n=4 rule or re-run ≥5 repeats; C5 "both estimators" rule; C11 4-round rule or re-run `--reps` ≥ 6; GPU memo "below MDI" readings at 0.94 %; #412's flagged choices. v2 catalogue qualification waits on the setup-baseline reference-host decision. Brain compile-drift follow-up filed as Mind `draft/bug/pyautobrain/profiling_compile_drift_point_vs_point.md`. Measuring repeats needs compute (not authorized).
- Next: human `/prm` #410 -> #411 -> #412, then close #362 and set this task complete. Completion is not inferred from PR-open.

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
