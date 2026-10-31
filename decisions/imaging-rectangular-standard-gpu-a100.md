# Designation: imaging/rectangular standard gpu_a100

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL gpu node (4 × A100 80GB PCIe; 124 cores, 885 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| ao | `jax_gpu_dense_fp64` **(optimal)** | 12.6 | 317.1 | gpus | match | [`lifecycle/d570569f32c953038fde`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/ao/jax_gpu_dense_fp64/hpc_a100/runtime.json) |
| ao | `jax_gpu_sparse_fp64` (secondary) | 4.27 | 937 | gpus | match | [`lifecycle/46db4990a22e25aee123`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/ao/jax_gpu_sparse_fp64/hpc_a100/runtime.json) |
| euclid | `jax_gpu_dense_fp64` **(optimal)** | 521 | 7.684 | gpus | match | [`lifecycle/456f7d65babc5524183a`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/euclid/jax_gpu_dense_fp64/hpc_a100/runtime.json) |
| euclid | `jax_gpu_sparse_fp64` (secondary) | 309 | 12.93 | gpus | match | [`lifecycle/bc5ed323618c58fc7682`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/euclid/jax_gpu_sparse_fp64/hpc_a100/runtime.json) |
| hst | `jax_gpu_dense_fp64` **(optimal)** | 162 | 24.68 | gpus | match | [`lifecycle/42f6a707360ce63b8150`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/hst/jax_gpu_dense_fp64/hpc_a100/runtime.json) |
| hst | `jax_gpu_sparse_fp64` (secondary) | 98.7 | 40.52 | gpus | match | [`lifecycle/cc3f3365b6ac65388a93`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/hst/jax_gpu_sparse_fp64/hpc_a100/runtime.json) |
| jwst | `jax_gpu_dense_fp64` **(optimal)** | 65.9 | 60.71 | gpus | match | [`lifecycle/ec69a200557ea8212e5e`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/jwst/jax_gpu_dense_fp64/hpc_a100/runtime.json) |
| jwst | `jax_gpu_sparse_fp64` (secondary) | 37.3 | 107.3 | gpus | match | [`lifecycle/bdffd9d6d157b3b66435`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/jwst/jax_gpu_sparse_fp64/hpc_a100/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- ao: jax_gpu_dense_fp64 12.6 vs jax_gpu_sparse_fp64 4.27 calls/s/node = 2.95x (tol 1%) SEP
- euclid: jax_gpu_dense_fp64 521 vs jax_gpu_sparse_fp64 309 calls/s/node = 1.68x (tol 4%) SEP
- hst: jax_gpu_dense_fp64 162 vs jax_gpu_sparse_fp64 98.7 calls/s/node = 1.64x (tol 1%) SEP
- jwst: jax_gpu_dense_fp64 65.9 vs jax_gpu_sparse_fp64 37.3 calls/s/node = 1.77x (tol 2%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `jax_gpu_dense_fp64`
- Secondary: `jax_gpu_sparse_fp64`
- Rule: Any imaging dataset with a rectangular pixelized source on an A100 node uses jax_gpu_dense_fp64, falling back to jax_gpu_sparse_fp64.
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: imaging-rectangular-standard-gpu-a100` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
