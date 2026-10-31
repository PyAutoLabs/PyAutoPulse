# Designation: imaging/rectangular standard cpu_many_core

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL ral node (236 cores, 921 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| ao | `jax_cpu_sparse_fp64` (secondary) | 0.378 | 76,818 | cores | match | [`lifecycle/d7020017fca2249bf32b`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/ao/jax_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| ao | `numba_cpu_sparse_fp64` **(optimal)** | 3.21 | 9,982 | memory | match | [`lifecycle/403420f8debaaa38956c`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/ao/numba_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| euclid | `jax_cpu_sparse_fp64` (secondary) | 31.9 | 910.6 | cores | match | [`lifecycle/4c53e409a27040f5d6a4`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/euclid/jax_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| euclid | `numba_cpu_sparse_fp64` **(optimal)** | not projected (peak_rss_gb not recorded (sacct recorded no MaxRSS for the .batch step (the task ended before the accounting sample))) | 282.5 | — | match | [`lifecycle/6060fdcfa2e5a4a0c168`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/euclid/numba_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| hst | `jax_cpu_sparse_fp64` (secondary) | 9.79 | 2,963 | cores | match | [`lifecycle/2b5e34f509175fd4d030`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/hst/jax_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| hst | `numba_cpu_sparse_fp64` **(optimal)** | 339 | 696.7 | cores | match | [`lifecycle/b62534053c00fb102bf4`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/hst/numba_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| jwst | `jax_cpu_sparse_fp64` (secondary) | 5.04 | 5,754 | cores | match | [`lifecycle/9bb2e30e94491253641b`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/jwst/jax_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |
| jwst | `numba_cpu_sparse_fp64` **(optimal)** | 140 | 1,688 | cores | match | [`lifecycle/304ac75d242dcbc2c22f`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/imaging/rectangular/jwst/numba_cpu_sparse_fp64/hpc_ral_cpu/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- ao: numba_cpu_sparse_fp64 3.21 vs jax_cpu_sparse_fp64 0.378 calls/s/node = 8.49x (tol 9%) SEP
- euclid: PER-CALL FALLBACK (['numba_cpu_sparse_fp64'] not projected)
- euclid: numba_cpu_sparse_fp64 3.54 vs jax_cpu_sparse_fp64 1.1 1/per-call = 3.22x (tol 5%) SEP
- hst: numba_cpu_sparse_fp64 339 vs jax_cpu_sparse_fp64 9.79 calls/s/node = 34.61x (tol 9%) SEP
- jwst: numba_cpu_sparse_fp64 140 vs jax_cpu_sparse_fp64 5.04 calls/s/node = 27.74x (tol 9%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `numba_cpu_sparse_fp64`
- Secondary: `jax_cpu_sparse_fp64`
- Rule: Any imaging dataset with a rectangular pixelized source on a many-core CPU node with no GPU uses numba_cpu_sparse_fp64, one serial likelihood per core (workers capped by node memory over peak RSS).
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: imaging-rectangular-standard-cpu-many-core` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- RAL CPU rows of 2a and 2d–2g ran on shared, loaded nodes (human ruling 2026-10-30); the 2b/2c RAL CPU rows are the quiet-node reruns (autolens_profiling#494).
- One instrument is ranked per call: its numba row has no peak RSS (sacct sampled no MaxRSS), so it has no node projection.
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
