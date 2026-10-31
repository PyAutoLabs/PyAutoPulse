# Designation: multi_dataset/delaunay standard cpu_many_core

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL ral node (236 cores, 921 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| hst | `jax_cpu_sparse_fp64` (secondary) | 4.67 | 6,214 | cores | match | [`lifecycle/f1dc379c56f5c2c7f32d`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/multi_dataset/delaunay/hst/jax_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| hst | `numba_cpu_sparse_fp64` **(optimal)** | 82.7 | 2,852 | cores | match | [`lifecycle/f57f23fc63823bcdf1bc`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/multi_dataset/delaunay/hst/numba_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- hst: numba_cpu_sparse_fp64 82.7 vs jax_cpu_sparse_fp64 4.67 calls/s/node = 17.73x (tol 9%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `numba_cpu_sparse_fp64`
- Secondary: `jax_cpu_sparse_fp64`
- Rule: A multi-dataset imaging fit (several datasets fitted together) with a Delaunay pixelized source on a many-core CPU node with no GPU uses numba_cpu_sparse_fp64, one serial likelihood per core (workers capped by node memory over peak RSS), falling back to jax_cpu_sparse_fp64.
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: multi-dataset-delaunay-standard-cpu-many-core` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- RAL CPU rows of 2a and 2d–2g ran on shared, loaded nodes (human ruling 2026-10-30); the 2b/2c RAL CPU rows are the quiet-node reruns (autolens_profiling#494).
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
