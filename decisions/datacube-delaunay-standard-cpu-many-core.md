# Designation: datacube/delaunay standard cpu_many_core

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL ral node (236 cores, 921 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| alma | `jax_cpu_sparse_fp64_wtilde` (secondary) | 2.03 | 14,294 | cores | match | [`lifecycle/8e374ab509e7626573da`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/alma/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 25.2 | 9,356 | cores | match | [`lifecycle/5800a501664b981824d4`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/alma/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma_high | `jax_cpu_sparse_fp64_wtilde` (secondary) | 1.31 | 22,051 | cores | match | [`lifecycle/6669e2835516e93361f1`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/alma_high/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| alma_high | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 3.8 | 17,643 | memory | match | [`lifecycle/3ea56488a996d6f0ffd1`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/alma_high/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| sma | `jax_cpu_dense_fp64_nufft` | 1.18 | 22,904 | memory | match | [`lifecycle/84cc85952546c05eabe2`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/sma/jax_cpu_dense_fp64_nufft/hpc_ral_cpu/runtime.json) |
| sma | `jax_cpu_sparse_fp64_wtilde` (secondary) | 2.25 | 12,907 | cores | match | [`lifecycle/649dfad640b1afce5631`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/sma/jax_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |
| sma | `numba_cpu_sparse_fp64_wtilde` **(optimal)** | 27.9 | 8,444 | cores | match | [`lifecycle/5b411896dcf5b1cc5853`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/datacube/delaunay/sma/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- alma: numba_cpu_sparse_fp64_wtilde 25.2 vs jax_cpu_sparse_fp64_wtilde 2.03 calls/s/node = 12.43x (tol 9%) SEP
- alma_high: numba_cpu_sparse_fp64_wtilde 3.8 vs jax_cpu_sparse_fp64_wtilde 1.31 calls/s/node = 2.89x (tol 9%) SEP
- sma: numba_cpu_sparse_fp64_wtilde 27.9 vs jax_cpu_sparse_fp64_wtilde 2.25 calls/s/node = 12.44x (tol 9%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `numba_cpu_sparse_fp64_wtilde`
- Secondary: `jax_cpu_sparse_fp64_wtilde`
- Rule: A datacube (interferometer channels fitted together) with a Delaunay pixelized source on a many-core CPU node with no GPU uses numba_cpu_sparse_fp64_wtilde, one serial likelihood per core (workers capped by node memory over peak RSS), falling back to jax_cpu_sparse_fp64_wtilde.
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: datacube-delaunay-standard-cpu-many-core` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- RAL CPU rows of 2a and 2d–2g ran on shared, loaded nodes (human ruling 2026-10-30); the 2b/2c RAL CPU rows are the quiet-node reruns (autolens_profiling#494).
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
