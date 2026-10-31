# Designation: interferometer/delaunay standard gpu_a100

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL gpu node (4 × A100 80GB PCIe; 124 cores, 885 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| alma | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 192 | 20.83 | gpus | match | [`lifecycle/8dada4df3a4ed30d1721`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| alma_high | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 62.8 | 63.71 | gpus | match | [`lifecycle/ba12584bdfe8c2e16f30`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma_high/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| jvla | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 8.6 | 465.2 | gpus | match | [`lifecycle/3c33efbabefe647c901b`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/jvla/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| sma | `jax_gpu_dense_fp64_nufft` (secondary) | 69.8 | 57.35 | gpus | match | [`lifecycle/ff5c53947f845ee5f2d8`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/sma/jax_gpu_dense_fp64_nufft/hpc_a100/runtime.json) |
| sma | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 352 | 11.36 | gpus | match | [`lifecycle/742eaf1292ed737e591e`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/sma/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- alma: jax_gpu_sparse_fp64_wtilde (only setup)
- alma_high: jax_gpu_sparse_fp64_wtilde (only setup)
- jvla: jax_gpu_sparse_fp64_wtilde (only setup)
- sma: jax_gpu_sparse_fp64_wtilde 352 vs jax_gpu_dense_fp64_nufft 69.8 calls/s/node = 5.05x (tol 1%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `jax_gpu_sparse_fp64_wtilde`
- Secondary: `jax_gpu_dense_fp64_nufft`
- Rule: Any interferometer dataset with a Delaunay pixelized source on an A100 node uses jax_gpu_sparse_fp64_wtilde, falling back to jax_gpu_dense_fp64_nufft. Untested: the GPU streaming route (measured up to jvla, 2.5e7 visibilities, on W~ sparse).
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: interferometer-delaunay-standard-gpu-a100` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
