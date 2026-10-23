Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autolens_profiling/cluster_pointsolver_speed.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: wiki `cluster_pointsolver.md` unchanged since `a5e5d77` (2026-09-27); it still points at the removed Mind draft path (now this file).
- VERIFIED: Mind epics.md now links this file as the cluster epic ledger; no new task issued since the human expansion of 2026-10-01; no open issue/PR or Mind claim.
- Next: pick one bounded phase: observable-overflow invalid-result policy + CI witness (autolens_workspace_test), or a representative-data baseline cell.


## Check-in 2026-10-13

- Campaign review: No campaign wiki/results change or new matching implementation claim found. Representative cluster baseline and observable-overflow policy remain unstarted. Choose one bounded phase; inherited single-source results do not qualify a representative cluster baseline.
- Task next step: Unissued, no claim. Pick one bounded phase per Mind epics.md: observable-overflow invalid-result policy + CI witness, or a representative-data baseline cell.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. Unissued, no claim. Pick one bounded phase per Mind epics.md: observable-overflow invalid-result policy + CI witness, or a representative-data baseline cell.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.

## Check-in 2026-10-23

- VERIFIED: phase 1 (cluster-scale robust PointSolver settings) MERGED: [autolens_profiling#436](https://github.com/PyAutoLabs/autolens_profiling/issues/436) → [#438](https://github.com/PyAutoLabs/autolens_profiling/pull/438) (`c8c9abb3`, 2026-10-22). Record: [complete/2026/10/cluster-pointsolver-robust-settings.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/cluster-pointsolver-robust-settings.md); ledger: [results/notes/cluster_pointsolver_campaign.md at c8c9abb3](https://github.com/PyAutoLabs/autolens_profiling/blob/c8c9abb30b51698343a15adb767f80c9d4640273/results/notes/cluster_pointsolver_campaign.md).
- Human decision DEFERRED 2026-10-22: the default initial scale stays 1.0″. See the Knowledge block below.
- VERIFIED (RAL `sacct` + log read 2026-10-23): the A2744 pilot leg, job 412573 (`cluster_pointsolver_pilot`, profiling `b39f7ab2`, CPU fp64, `ral`), is **FAILED** after 03:33:07 with MaxRSS 85.5 GB. It completed 16 diagnostic rows. Row 17 (`tight_s1_p0.001`) and the two capacity controls died on LLVM `Cannot allocate memory` / `Failed to materialize symbols`. No JSON, PNG or memory trace was written.
- A2744 ordering (synthetic prior-median model, 7 sources, 3 judged draws, 69 oracle roots): production 1.0″ misses 2/69 (both stress), 0.5″ misses 3, 0.7″ misses 5, 2.0″ misses 8. Truth-bbox extents miss 9–11. This is the opposite ordering to `simple`, so the initial-scale ranking is dataset-dependent.
- RSS attribution (owed follow-up, now done): RSS climbs 8.3 → 39.4 GB over 16 rows while live JAX arrays stay ~0 MB. The growth is retained compiled executables (one 191-component multi-plane solver JIT per row, kept for interleaved timing) plus per-row compile transients (peak 22 → 81.5 GB). The harness must release executables between rows, or run one row per process, before any A2744 full sweep. No resubmission is authorized.
- Next bounded task: the starting-grid / close-member-image Mind draft ([cluster_pointsolver_starting_grid_close_member_image.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/draft/research/autolens_profiling/cluster_pointsolver_starting_grid_close_member_image.md)) via start_dev. One task, no bulk queue.
- Phase 2 (workspace_test CI witnesses) still has nothing accepted to distil. The old `point_solver_profiling_cells` coverage reconciles onto phase 1's harness (`scripts/cluster/image_plane/robust_settings_sweep.py`) when the next profiling cell is issued; no duplicate cell.
- Review date does not refresh measurement dates. This check-in authorizes no compute, default change or merge. [Full dated check-in](../checkins/2026-10-23.md).

## Knowledge (2026-10-22): phase 1, cluster-scale robust PointSolver settings

**Sources.** [autolens_profiling#436](https://github.com/PyAutoLabs/autolens_profiling/issues/436);
ledger `results/notes/cluster_pointsolver_campaign.md`; sweep JSON
`results/breakdown/cluster/robust_settings_sweep_simple_hpc_ral_cpu_fp64.json` (RAL job 412572,
Xeon 8490H, CPU fp64, profiling `b39f7ab2`, PyAutoLens `c90eceb0`).

**Ground truth.** The oracle is independent of the triangle solver. It samples the multi-plane
lens-equation residual densely, Newton-polishes each basin and certifies roots below 1e-10″
residual and 1e-6″ stability. It is calibrated to 2.84e-8″ on the 1a closed-form quad and the
1c/1d near-cusp fixture.

**Result (`simple`, 13 components, 3 planes, 2 sources, 101 draws).** No setting is admissible.
Production-extent rows cover 306/306 prior roots and miss 2–6 of 300 stress roots. Every miss
is a close high-|μ| pair, 0.33–0.76″ apart, on stress draws 53, 73 and 81 (one pair straddles
the radial critical curve). Initial scale 0.5″/0.7″ misses 2 at 0.78×/0.75× the control's
speed. The production 1.0″ misses 5 (5.29 ms per warmed two-source solve) and 2.0″ misses 6
(1.30×). Precision 0.01 vs 0.001, `MAX_CONTAINING_SIZE` 20/40/60 and backend
(NumPy/JIT/vmap) do not change coverage. The uncapped containing count reaches at most 7, so
there is no overflow at cap 20. Eager JAX is unusable (projected row wall over cap). Truth-bbox
extents miss 49–63 stress roots because the images move with the model. Peak RSS 4.3 GB.

**Verdict.** DEFERRED (human, 2026-10-22). The 2-miss, ~0.77×-speed 0.5″/0.7″ start vs the
5-miss 1.0″ production control is re-decided after the starting-grid draft and the A2744 pull.
No default was changed; 0.5″ is the working answer if the choice is forced earlier.

**A2744 pilot (pulled 2026-10-23).** RAL job 412573 (profiling `b39f7ab2`, CPU fp64, `ral`) is
FAILED after 16 diagnostic rows (03:33:07, MaxRSS 85.5 GB). The dataset is an A2744-geometry
synthetic model at prior medians, not a fitted cluster model: 7 sources (z 1.69–5.66), 3 judged
draws (reference, prior, stress), oracle calibration 2.84e-8″, 69 stable oracle roots (prior 49,
stress 20). Coverage: production 1.0″ (p0.01 and the p0.001 control) 67/69, missing 2 stress
roots; 0.5″ 66/69; 0.7″ 64/69; 2.0″ 61/69; truth-bbox extents 58–60/69. Precision 0.01 vs 0.001
never changes coverage; no duplicates or spurious images; the uncapped containing count peaks
at 9, so cap 20 never binds. The ordering is the opposite of `simple` (0.5″/0.7″ best there), so
the initial-scale ranking is dataset-dependent. The deferred decision is unchanged (default
stays 1.0″) and the 0.5″ "working answer if forced" is weaker. Row 17 (`tight_s1_p0.001`) and
the two capacity controls are invalid: LLVM `Cannot allocate memory` → `JaxRuntimeError:
Failed to materialize symbols` → job killed. The backend rows and timing rounds were never
reached and no JSON was written, so there is no speed claim. RSS rose 8.3 → 39.4 GB over 16 rows
(2–4 GB per row) with live JAX arrays ~0 MB. The growth is retained compiled executables (one
191-component multi-plane solver JIT per row, kept for interleaved timing) plus compile
transients (peak 22 → 81.5 GB); on `simple` (13 components) the same mechanism cost only
1.5 → 4.3 GB. Resubmission needs explicit human authorization.

**Open.** The starting-grid / close-member-image question is in its own Mind draft
(`cluster_pointsolver_starting_grid_close_member_image.md`). The sweep harness must release
executables between rows (or run one row per process) before any A2744 full sweep. The human's
Pulse profiling programme may revisit this goal.

---

# Cluster PointSolver — robustness, analysis settings and performance

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
- autolens_workspace_test
- PyAutoLens
- PyAutoArray
- PyAutoGalaxy
Themes:
- cluster
- point-source
- profiling
- jax
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised
Consequence: judge
Review-minutes: 20
Unattended: ready
Epic: cluster-pointsolver-speed
Filed: 2026-09-26
Parent-record: complete/2026/09/point-source-cpu-p3.md

## Status and ownership — approved 2026-10-01

Canonical planning ledger for epic `cluster-pointsolver-speed` (identifier
retained; display title broadened). `autolens_profiling` is the execution/evidence
home for both “make autolens fast” and “which settings make the analysis robust”.
This expands the unstarted cluster speed campaign; it does not restart completed
single-source work. The profiling repo's `wiki/campaigns/cluster_pointsolver.md`
is the earlier speed-only survey, to be reconciled when the first campaign task
starts; this Mind contract governs the newly approved scope in the meantime.

Transferred from Source & Cluster arc:
- `draft/bug/autolens/point_solver_error_bisect_health.md`: remaining phase-1
  overflow, accuracy/identity and regression obligations, historical-bisect
  limitation disposition. Completed 1a–1d records remain in their original arc.
- `draft/research/autolens_profiling/point_solver_profiling_cells.md`: old phase-2
  coverage gaps, reconciled with current profiling taxonomy and the already
  completed single-source campaign before any issue is filed.
- Forward ShapeSolver rehabilitation/retirement and its finite-source convergence
  tests from arc phase 6. Primary pixel-based area magnification stays in the arc.

No task in this programme is issued by this transfer. Issue ONE bounded task at
a time as its predecessor nears shipping; not the umbrella and not a bulk queue.

## Working contract

1. **Robustness/settings evidence belongs in autolens_profiling.** Measure initial
   grid scale, extent, target precision, capacity, backend/dtype and applicable
   source/redshift regimes against independent numerical references. Publish the
   supported settings and their tested domain, unresolved outcomes, cost and
   provenance together. Shared library repairs remain general, not cluster-only.
2. **Numerical integration guarantees belong in autolens_workspace_test.** Distil
   every accepted repair/settings claim into bounded reproducible regressions:
   positions, per-image coverage, overflow, unresolved multiplicity, eager/JIT/vmap
   and registered-tracer/gradient behavior where affected. Name and wire a CI lane:
   cheap deterministic witnesses in required PR smoke; expensive coverage in the
   scheduled/release suite. A standalone opt-in diagnostic with no CI consumer is
   not completion of this regression obligation. Existing 1c/1d cells remain
   historical evidence in workspace_test; do not move or duplicate them wholesale.
3. **Performance measurement can begin before all repairs finish.** Label failing
   cases diagnostic/invalid and retain their timings, but exclude them from
   accepted speed-up and robust-settings claims. Matching the old likelihood is
   insufficient: require independent accuracy/coverage, no silent truncation and
   relevant derivative/batch checks before accepting an optimisation. Record
   compile, first-call and warmed costs separately on pinned hardware.
4. **Finite acceptance target.** Specify supported workloads/tolerances first;
   detect overflow, establish per-image accuracy/coverage, expose unresolved cases,
   and verify backend behavior. Do not use “trusted everywhere” as an unbounded
   exit condition or silently change scientific tolerances to win speed.
5. **Handoffs.** Profiling evidence → bounded library repair → CI regression →
   settings recommendation. Downstream Source & Cluster tasks depend on the
   concrete capability they use, not completion of this whole programme.

## Next task selection and workstreams

Next production candidate: observable containment-overflow contract under eager,
JIT and vmap, including caller invalid-result behavior and CI witnesses. Recheck
claims and approve the API design through start_dev before issuing it. The earlier
streaming #600 Array claim has closed; that is not a standing conflict waiver.
Representative cluster data and baseline profiling below can be scoped without
waiting for every accuracy question; failing configurations remain labelled.

Accuracy/identity work uses 1c/1d's counterexamples: three non-converged false
accepts from the local correction screen; adding convergence loses closest-cusp
coverage. Investigate safeguarded refinement/nonlinear error control, not another
unqualified distance/residual rule. Forward ShapeSolver work requires its own
bounded current-code audit, backend dispatch, per-image area/convergence evidence
and CI tests, or an explicit retirement decision. Preserve the old phase-6
requirement to compare any promoted forward implementation with independent
simulated area truth/pixel-based results; it no longer blocks the primary API.

Completed evidence: `complete/2026/09/point-solver-error-audit.md`,
`complete/2026/09/point-solver-padding-backend.md`,
`complete/2026/10/point-solver-duplicate-policy.md`,
`complete/2026/10/point-solver-image-accuracy.md`.

## User-approved expansion (verbatim)

Ok  I agreem autolens_profiling is evolving into "make autolens fast" but also "these are the settings I need to ensure the analysis is robust" so this work is also more and more belonging there, albeit we need numerical integration tests in autolens_workspace_test which ensure this all makes it way into CI. Update accordingly and then wrap up

## User request (verbatim)

Lets push through all work on single source, working in autolens_profiling/scritps/point_source, we will do cluster use case as as eparate epic so maybe move this as part of an intake that will do that whole thing starting from working out the data and likelihood_breakdown.

## Profiling workstream — cluster data and a released-code baseline

No lever is ranked until this exists. Deliverables:

1. **Work out the cluster data.** Pick one or more representative cluster datasets and justify them
   against real cluster modelling in `@autolens_workspace` (`scripts/cluster/`). For each, record:
   - the number of sources and source planes / redshifts;
   - the number of multiple images per source;
   - the lens model components (BCG, cluster-scale halo(s), member galaxies — profile types and
     counts, e.g. dPIE / NFW);
   - the solver grid (extent, `pixel_scale_precision`) production cluster fits actually use.

   The current profiling case (`dataset/cluster/simple`, gitignored and auto-simulated: 13 mass
   components, 3 planes, 2 sources) is a starting point, not a verdict.
2. **Audit and refresh `@autolens_profiling` `scripts/cluster/likelihood_breakdown/`.**
   `image_plane.py` and `source_plane.py` both exist; check them against the point-source
   instrument (`scripts/point_source/likelihood_breakdown/` plus the shared
   `scripts/misc/likelihood_breakdown/{timing,provenance,_profile_cli}.py`). Then bring them to the
   campaign measurement contract:
   - fused production likelihood control;
   - separated compile vs first vs warmed timings;
   - interleaved medians + CI;
   - `source_revisions`, thread environment, XLA memory and FLOPs recorded;
   - a per-step / per-component split (step 0 vs refinement, deflections vs bookkeeping, per
     source).
   - **Precision caveat:** the current cell runs `pixel_scale_precision=0.01` (to keep compile at
     minutes), not production `0.001`. Measure both, or justify the choice explicitly.
3. **Baseline on released code** (2026.9.26.1 or later, which carries point-source p2 + p3) on a
   pinned RAL CPU node (Xeon 8490H, `--nodelist`; check `sinfo` first), with an A100 row. Update
   the README dashboards. Record the per-step wall-time split, which then ranks phase 2+.

## Carried evidence (from point-source p1–p3; records `complete/2026/09/point-source-cpu-p{1,2,3}.md`, ledger `autolens_profiling/results/notes/point_source_cpu_campaign.md`)

- **Two-source cluster solved likelihood, per phase:**
  - p1 RAL baseline (Xeon 8490H): fused plain 128.05 ms, fused solved 134.52 ms, per-source solves
    110 / 115 ms. Per-source solves exceed the fused call, a fusion-boundary effect.
  - p2 vertex-dedup removal (RAL job 350582, EPYC 7763): 155.22 → 78.32 ms (1.98×). The control is
    +15–20 % from the host alone, so pin the node.
  - p3 static step-0 lattice (RAL job 350636, Xeon 8490H pinned): 47.36 → 9.085 ms (5.21×); 3.9–4.5×
    with constant folding on.
  - FLOPs: 184.2M → 139.4M → 39.5M.
  - XLA temp memory: 91.6 → 22.6 MB (A100 42.1 → 6.35 MB).
- **Lattice:** the 200×200 @ 0.7″ cluster step-0 lattice now deflects **46 516 of 276 507** unique
  vertices.
- **Where the cost is now (FLOP estimate, not measured):** deflections of the 13-component lens
  dominate every cluster step. Step 0 is ≈ 51 % of cluster FLOPs.
- **Lever: dPIE/NFW deflection cost.** This is likely a PyAutoGalaxy phase, separately scoped.
  `@autolens_profiling` `scripts/lens/deflections/` is **NumPy-only** and has **no dPIE spec**, so a
  JAX deflection cell with dPIE/NFW specs is a prerequisite for measuring it.
- **Lever: grid-extent guidance.** Stronger at cluster scale, where it acts on the ≈ 51 % step-0
  share plus containment. It needs image-completeness evidence across a prior, with each extent
  reported as its own configuration and never substituted into a speed row.
- **Unmeasured control:** direct deflections on the full 276 507-point cluster input. The old
  "cluster solve is at its deflection bound" claim was extrapolated, not measured.
- **Single-source phase 4a** (solver-config sweep: initial scale × precision,
  `MAX_CONTAINING_SIZE`, extent) may produce methods or findings reusable here. Read its ledger
  section before planning phase 2.

## Measurement contract

This inherits the point-source campaign contract (phase-4 prompt, "Campaign contract (2026-09-19)"):
- exact revisions recorded;
- interleaved A/B on identical hardware with distinct function objects + `jax.clear_caches()`;
- a fused production control;
- a correctness gate before any speed claim: bit-identical likelihood, solved positions,
  multi-source / multiplane coverage, JVP / vmap parity;
- negative results recorded;
- one bounded phase per issue and PR.

## Later performance candidates (re-rank after the baseline)

2. Deflection-cost lever (JAX dPIE/NFW deflection cell first; PyAutoGalaxy change separately scoped).
3. Cluster grid-extent guidance with completeness evidence.
4. Whatever the phase-1 split exposes (per-source batching, multiplane bookkeeping, capacity).
