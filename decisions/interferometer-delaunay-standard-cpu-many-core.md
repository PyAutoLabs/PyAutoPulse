# Designation: interferometer/delaunay standard cpu_many_core

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL ral node (236 cores, 921 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| alma | `jax_cpu_sparse_fp64_wtilde` (secondary) | 13.7 | 2,121 | cores | match | [`lifecycle/60747d6f7a1867da50c9`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 308 | 764.9 | cores | match | [`lifecycle/5e9d64046821795b4651`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma_high | `jax_cpu_sparse_fp64_wtilde` (secondary) | 3.81 | 7,601 | cores | match | [`lifecycle/d54c6814c51c381564cf`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma_high/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma_high | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 25.3 | 9,329 | cores | match | [`lifecycle/bfe464d85eab437c56be`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/alma_high/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| jvla | `jax_cpu_sparse_fp64_wtilde` (secondary) | 0.564 | 51,435 | cores | match | [`lifecycle/757d2c2d7167cdef0457`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/jvla/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| jvla | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 1.22 | 63,799 | memory | match | [`lifecycle/e63a97d451e1633c91aa`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/jvla/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| sma | `jax_cpu_dense_fp64_nufft` | 4.64 | 5,822 | memory | match | [`lifecycle/284efdc05b70e06e060a`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/sma/jax_cpu_dense_fp64_nufft/hpc_ral_cpu/runtime.json) |
| sma | `jax_cpu_sparse_fp64_wtilde` (secondary) | 37 | 784.6 | cores | match | [`lifecycle/00838694b2c3c955a644`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/sma/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| sma | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 845 | 279.3 | cores | match | [`lifecycle/b2d01ef74bf71e49d774`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/delaunay/sma/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- alma: numba_cpu_sparse_fp64_wtilde 308 vs jax_cpu_sparse_fp64_wtilde 13.7 calls/s/node = 22.57x (tol 3%) SEP
- alma_high: numba_cpu_sparse_fp64_wtilde 25.3 vs jax_cpu_sparse_fp64_wtilde 3.81 calls/s/node = 6.63x (tol 9%) SEP
- jvla: numba_cpu_sparse_fp64_wtilde 1.22 vs jax_cpu_sparse_fp64_wtilde 0.564 calls/s/node = 2.17x (tol 9%) SEP
- sma: numba_cpu_sparse_fp64_wtilde 845 vs jax_cpu_sparse_fp64_wtilde 37 calls/s/node = 22.86x (tol 5%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `numba_cpu_sparse_fp64_wtilde`
- Secondary: `jax_cpu_sparse_fp64_wtilde`
- Rule: Any interferometer dataset with a Delaunay pixelized source on a many-core CPU node with no GPU uses numba_cpu_sparse_fp64_wtilde, one serial likelihood per core (workers capped by node memory over peak RSS), falling back to jax_cpu_sparse_fp64_wtilde. Untested: CPU streaming and the MGE DFT route.
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: interferometer-delaunay-standard-cpu-many-core` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- RAL CPU rows of 2a and 2d–2g ran on shared, loaded nodes (human ruling 2026-10-30); the 2b/2c RAL CPU rows are the quiet-node reruns (autolens_profiling#494).
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
