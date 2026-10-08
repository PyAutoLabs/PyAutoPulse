# Keep Jacobi PDIP as the Mapper default and raw+polish as the MGE-only default

Date: 2026-10-08
Decision maker: James Nightingale
Decision source: chat, 2026-10-08, in the PyAutoPulse profiling check-in. The human stated the goal ("I want a fast solution but it also needs to be stable for all likelihood functions"), chose the bounded evidence step over wrapping up or switching the default on MGE-only evidence ("Lets do option 2"), and after the Mapper-corpus result accepted the recommendation to keep Jacobi for Mapper inversions ("I agree with your decision"; recorded on the human's instruction).

## Campaign

Linear-solver programme of the `linear-solver` campaign (Pulse task `mge_nnls_fix_pyautoarray_571_slam_60`; project autolens_profiling, `scripts/lens/solver/`). Every PyAutoLens likelihood with linear light profiles or a pixelization ends in a non-negative least-squares solve of `(curvature_reg_matrix, data_vector)`. The library runs two JAX primal-dual interior-point (PDIP) modes: the raw system with a data-scaled tolerance and a Jacobi-space polish (`pdip_raw`, the MGE-only default since PyAutoArray#595) and Jacobi-preconditioned PDIP (`pdip_jacobi`, the default whenever a Mapper is present). The question was whether one solver could be both fast and stable for every likelihood, and in particular whether the Mapper default should move off Jacobi on GPU.

## Evidence

All measurements at library tag 2026.10.7.1 (PyAutoNerves c5ade605, PyAutoFit 710f4b34, PyAutoArray ccddfba6, PyAutoGalaxy b4946b8a, PyAutoLens b6bf543c), fp64, JAX 0.10.2; CPU rows on the laptop (WSL2, i9-10885H) from tag worktrees, GPU rows on RAL A100 80GB nodes from a private checkout. Ledger: `results/notes/linear_solver_accuracy_2026_09.md`; research page: `wiki/research/jacobi_a100_batched_divergence.md`.

- **MGE corpus (81 SLaM systems, n = 60).** Phase 3a (autolens_profiling#394, merge a55dcacb; A100 job 397475): `pdip_raw` reproduces its CPU rows on the A100 (max |Δ flux_inactive_rel| 5.4e-14, iterations identical 81/81) but stays inadmissible under the pre-registered rule on two systems; `pdip_jacobi` diverges on 29 (CPU) / 19 (A100) systems. Phase 3b (#396, merge 86cb1460; A100 job 398249): per-evaluation cost inside `jit(vmap)`, compile excluded, `pdip_raw` 0.19 ms vs `pdip_jacobi` 0.37 ms at batch 50 on the A100, because one diverging Jacobi lane pins the whole batch at the 50-iteration cap.
- **Cause of the A100-only batched/unbatched difference.** Phase 4a (#398, merge fe9ca472; A100 job 399050): deterministic, batch-shape-dependent rounding in the A100 Cholesky (`cho_factor`/`cho_solve` differ between batched and single solves on 50/50 lanes from the initialisation step at ~1e-15 relative), amplified to order one within 1–2 iterations only on Jacobi-unstable systems; not nondeterminism (the deterministic-ops flag changed no bit), not a `vmap` defect; `pdip_raw` and `certified` stay at ≤ 3e-12 with identical flags.
- **Mapper corpus (phase 5, issue #399; A100 job 399225, 6:20).** Three new groups of 8 near-truth systems: `delaunay_hst` (n = 1500), `rectangular_hst` (n = 1369), `slam_mixed_hst` (lens 2×20 MGE + Delaunay source, the production SLaM source_pix configuration, n = 1540). `pdip_jacobi` converged on 24/24 systems with 0/24 A100 batch-sensitive lanes (max |Δ| 1.5e-12). `pdip_raw` is admissible under the phase-1 rule, stated as extended to this corpus, on Delaunay and mixed; both PDIP modes fail criterion 2 on rectangular. `certified` fails on mixed and rectangular. Per-evaluation cost at batch 8 on the A100, compile separate: `pdip_raw` 1.05× (Delaunay), 1.62× (rectangular), 1.15× (mixed) the Jacobi cost. The phase-5 rows were delivered in PR #400 (commit 70e8a9f) and re-landed with the corpus files kept out of git; the measurements are unchanged.
- **Limitations.** All Mapper vectors are near-truth (four near-truth vectors plus two noise rescalings); wide-prior systems as sampled early in a search are unmeasured. No interferometer group (no importable capture harness). On the laptop CPU at n ~ 1500, batched and unbatched Jacobi differ by up to 4.2e-13 without changing iterations or flags (bit-identical at n = 60); not localised. Why the mixed systems stay Jacobi-stable despite carrying signal-free MGE columns is not established.

## Options considered

- **A. Keep Jacobi as the Mapper default and document it** (chosen). No library change; the known weakness is confined to Jacobi-unstable systems, of which the Mapper corpus contained none.
- **B. XLA deterministic-ops flag.** Ruled out by phase 4a: the effect is not nondeterminism.
- **C. Tolerance or iteration-cap change for Jacobi.** Not expected to help: sensitive lanes go order-one within two iterations, before any stopping test.
- **D. Move the Mapper default to raw+polish or certified.** Would give one solver for every likelihood, but adds no stability the measured Mapper systems need, costs 5–62 % more per evaluation, and raw+polish fails on rectangular while certified fails on mixed and rectangular.
- **E. One lowering for batched and single solves.** Bit-parity only, not stability.

## Decision

Keep the released configuration: `pdip_jacobi` wherever a Mapper is present (pixelized and mixed inversions, CPU and GPU) and `pdip_raw` with polish for MGE-only inversions. Document the batch-shape rounding behaviour rather than change a default. No tolerance, cap or pin changes. Phase 5 is the programme's last evidence phase for this question.

## Implications

- Nothing ships from this decision; it confirms the defaults already released in 2026.10.7.1 and the SLaM pipeline configuration that depends on them.
- GPU `vmap` batches and single re-fits of a Mapper system agree to rounding level and fully in iterations and flags on every measured system; on a Jacobi-unstable system (none seen among Mapper systems) they could differ, and the research page says so.
- Known accuracy gaps are recorded, not resolved: `pdip_raw` on two MGE corpus systems and both PDIP modes on the rectangular group fail criterion 2 of the phase-1 rule.
- The research page and the campaign wiki hold the decision table and the Mapper evidence for the next revisit.

## Revisit conditions

- A Mapper or mixed system, in a wide-prior or production search, found Jacobi-unconverged or batch-sensitive.
- An interferometer corpus (W-tilde systems) once a capture harness exists.
- A library change to the PDIP primitives, the Jacobi scaling or the polish rule, or a JAX/cuSOLVER change that alters the batched Cholesky path.
- A rectangular-mesh accuracy study, if criterion-2 failures there matter in practice.

## History

First decision on this question. No supersession.
