# Keep the 1.0″ PointSolver starting grid for cluster fits, with a validation check

Date: 2026-10-23
Decision maker: James Nightingale
Decision source: Human decision in chat on 2026-10-23 ("keep the 1.0″ starting grid"), taken after the phase-1 decision was DEFERRED on 2026-10-22 pending the starting-grid follow-up and the A2744 pull. Recorded in Mind [complete/2026/10/cluster-pointsolver-starting-grid.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/cluster-pointsolver-starting-grid.md).

## Campaign

This decision belongs to the cluster PointSolver campaign, task
[`cluster_pointsolver_speed`](../tasks/cluster_pointsolver_speed.md). Phase 1
([autolens_profiling#436](https://github.com/PyAutoLabs/autolens_profiling/issues/436) →
[#438](https://github.com/PyAutoLabs/autolens_profiling/pull/438)) measured which triangle-solver
settings find every multiple image of cluster-scale point sources. The open question was the
step-0 initial grid scale: the production 1.0″ against a finer start.

Every result below is judged against an independent oracle that samples the multi-plane
lens-equation residual densely and Newton-polishes each root (calibrated to 2.84e-8″). It is not
the triangle solver.

## Evidence

Ledger: [results/notes/cluster_pointsolver_campaign.md at `03d36c81`](https://github.com/PyAutoLabs/autolens_profiling/blob/03d36c810b2a4f7d31342d9a75f46cd7fe10f43a/results/notes/cluster_pointsolver_campaign.md).
The three inputs use different models and hardware; their numbers are not interchangeable.

- **`simple` sweep (phase 1).** Synthetic `dataset/cluster/simple`: 13 components, 3 planes,
  2 sources, 101 judged draws. RAL job 412572, Xeon 8490H, CPU fp64, production extent
  100×100 @ 1.0″. All rows cover 306/306 prior roots. Of 300 stress roots, 0.5″ and 0.7″ miss 2,
  the production 1.0″ misses 5 and 2.0″ misses 6. Warmed two-source solve: 1.0″ 5.29 ms, 0.5″
  6.82 ms (0.78× speed), 0.7″ 7.02 ms (0.75×). No row is admissible. Mind record
  [cluster-pointsolver-robust-settings.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/cluster-pointsolver-robust-settings.md).
- **A2744 pilot.** A2744-geometry synthetic model at prior medians (not a fitted cluster model),
  7 sources, 3 judged draws, 69 oracle roots. RAL job 412573, CPU fp64, pulled 2026-10-23. The job
  FAILED after 16 diagnostic rows on LLVM memory exhaustion, so there is no timing claim. Coverage:
  1.0″ misses 2/69, 0.5″ 3, 0.7″ 5, 2.0″ 8. The ordering is the opposite of `simple`.
- **Starting-grid follow-up** ([#439](https://github.com/PyAutoLabs/autolens_profiling/issues/439) →
  [#440](https://github.com/PyAutoLabs/autolens_profiling/pull/440), merged `03d36c81`; Mind
  [cluster-pointsolver-starting-grid.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/cluster-pointsolver-starting-grid.md)).
  autolens_visualization cluster model, laptop CPU fp64, 17 judged draws, diagnostic timings.
  The workspace 1.0″ grid loses `point_0`'s central image 0.39″ from `main_1`'s core, and so does
  every scale down to 0.3″. Only 0.2″ finds it (60.5 ms vs 7.4 ms warmed at 1.0″, ~8×), and 0.2″
  still misses 3/108 roots. Six draw-sources are found at a coarser scale and lost at a finer one.
  No single-separation rule holds over 236 draw-sources. The solver also returns spurious
  candidates (residual 0.04″) on `r_core = 0` member cores.

## Options considered

- **0.5″ start.** Fewest misses on `simple` (2) at ~0.77× speed, but 3 misses on A2744 (more than
  1.0″) and it does not find the viz model's central image.
- **Fixed 0.2″ start.** ~8× the per-solve cost (laptop) and still misses 3/108 viz roots.
- **Separation-based scale rule.** Unsupported: "scale ≲ separation / 1.06" is contradicted, and
  the only uncontradicted form rests on two synthetic models.
- **Keep 1.0″ and add a validation check.** Every observed image must have a solved counterpart;
  otherwise re-solve on a small fine grid around it and say so. Drop candidates whose
  source-plane residual exceeds the solver tolerance.

## Decision

Keep the 1.0″ starting grid as the production default, and adopt the validation check as the
mitigation for missed images. This closes the phase-1 decision deferred on 2026-10-22.

## Implications

No library or workspace default is changed by this record. The validation check is a Mind draft
(`draft/feature/autolens_workspace/cluster_point_solver_validation_check.md`, unissued). The
spurious-core candidates are a separate library task
(`draft/feature/autolens/point_solver_spurious_core_candidates.md`, start_dev in progress), next.
The solver is not in the likelihood (`FitPositionsSourceSolved` traces the observed images), so a
costly check at validation/visualization time does not slow fits.

## Revisit conditions

Evidence comes from synthetic models only; there is no fitted A2744 reference tracer, and the
A2744 pilot covers 3 draws without timings. A full A2744 sweep (needs a reference tracer and
human authorization), a fitted cluster model, or a validation check that fires often in practice
would reopen the choice.

## History

First record for this choice. It follows the phase-1 deferral (2026-10-22) recorded in the task
and the profiling ledger.
