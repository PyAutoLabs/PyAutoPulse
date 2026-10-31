# Designation: multi_dataset/delaunay standard gpu_a100

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL gpu node (4 × A100 80GB PCIe; 124 cores, 885 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| hst | `jax_gpu_dense_fp64` **(optimal)** | 22.7 | 176.3 | gpus | match | [`lifecycle/b5dea27fcaf8b14ec9bb`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/multi_dataset/delaunay/hst/jax_gpu_dense_fp64/hpc_a100/runtime.json) |
| hst | `jax_gpu_sparse_fp64` (secondary) | 19.6 | 204.1 | gpus | match | [`lifecycle/b14372bc431d168fa7ff`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/multi_dataset/delaunay/hst/jax_gpu_sparse_fp64/hpc_a100/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- hst: jax_gpu_dense_fp64 22.7 vs jax_gpu_sparse_fp64 19.6 calls/s/node = 1.16x (tol 0%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `jax_gpu_dense_fp64`
- Secondary: `jax_gpu_sparse_fp64`
- Rule: A multi-dataset imaging fit (several datasets fitted together) with a Delaunay pixelized source on an A100 node uses jax_gpu_dense_fp64, falling back to jax_gpu_sparse_fp64.
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: multi-dataset-delaunay-standard-gpu-a100` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
