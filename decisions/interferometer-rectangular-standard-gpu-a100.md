# Designation: interferometer/rectangular standard gpu_a100

Date: 2026-10-31
Decision maker: James Nightingale
Decision source: AskUserQuestion answer "Approve all 39 (Recommended)" in the ~/Science Claude Code session, 2026-10-31, on the re-derived proposals (PyAutoMind `draft/research/autolens_profiling/likelihood_lifecycle_p3_designation_proposals.md`, "Re-derivation 2026-10-31" and Appendix B). Recorded under PyAutoPulse#83.

## Campaign

Epic `likelihood-lifecycle`, phase 3 (day zero): one designation per likelihood × regime × hardware class, made by the human from measured, parity-checked cells. Evidence: autolens_profiling `dashboard/catalogue.json` at [`c218a428`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/dashboard/catalogue.json) (PR #496 head, the day-zero rows), on the RAL gpu node (4 × A100 80GB PCIe; 124 cores, 885 GB).

## Evidence

| instrument | setup | projected calls/s per node | per call (ms) | bound by | parity | record |
|---|---|---|---|---|---|---|
| alma | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 81.7 | 48.97 | gpus | match | [`lifecycle/fe32c3ee13ad9afc455c`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/rectangular/alma/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| alma_high | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 49.4 | 81.06 | gpus | match | [`lifecycle/2ab9504c46bb8170ba54`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/rectangular/alma_high/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| jvla | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 8.77 | 456.3 | gpus | match | [`lifecycle/220d076d8421130e83cf`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/rectangular/jvla/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |
| sma | `jax_gpu_dense_fp64_nufft` (secondary) | 77 | 51.98 | gpus | match | [`lifecycle/e44acbf15a2387706fa1`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/rectangular/sma/jax_gpu_dense_fp64_nufft/hpc_a100/runtime.json) |
| sma | `jax_gpu_sparse_fp64_wtilde` **(optimal)** | 593 | 6.748 | gpus | match | [`lifecycle/a39d6114339d546f6bd6`](https://github.com/PyAutoLabs/autolens_profiling/blob/c218a428cb20c8bb958b0d8462c3a8b8e196d152/results/interferometer/rectangular/sma/jax_gpu_sparse_fp64_wtilde/hpc_a100/runtime.json) |

Separation (pre-registered axis, human Q1/Q3 2026-10-30: rank by projected calls/s per node; separate when the winner beats the runner-up by more than the larger recorded p10–p90 spread, else 9 %): **separated**.

- alma: jax_gpu_sparse_fp64_wtilde (only setup)
- alma_high: jax_gpu_sparse_fp64_wtilde (only setup)
- jvla: jax_gpu_sparse_fp64_wtilde (only setup)
- sma: jax_gpu_sparse_fp64_wtilde 593 vs jax_gpu_dense_fp64_nufft 77 calls/s/node = 7.70x (tol 2%) SEP

## Options considered

The setups in the table, ranked on the pre-registered axis; per-call latency is secondary evidence.

## Decision

- Optimal: `jax_gpu_sparse_fp64_wtilde`
- Secondary: `jax_gpu_dense_fp64_nufft`
- Rule: Any interferometer dataset with a rectangular pixelized source on an A100 node uses jax_gpu_sparse_fp64_wtilde, falling back to jax_gpu_dense_fp64_nufft. Untested: the GPU streaming route (measured up to jvla, 2.5e7 visibilities, on W~ sparse).
- Basis: projected.

## Implications

autolens_profiling rows cited here are re-declared `class: optimal` with `decision_id: interferometer-rectangular-standard-gpu-a100` by the producer (next phase-3 task); `catalogue/provisional_designations.json` is retired in favour of these records. Recording does not change library defaults; phase 5 generates the library rule table from these records.

## Revisit conditions

- Projected throughput is an upper bound: workers × η / per call with η = 1.0 declared, unmeasured until phase 4 (`basis: projected`, Q4 option a). Nautilus `n_batch` and shared memory bandwidth are not modelled.
- Day-zero environment: tag 2026.10.25.1 (private checkout), jax/jaxlib 0.11.2 with `--xla_cpu_multi_thread_eigen=false` on CPU legs; numba rows carried (human Q7, 2026-10-30). JAX CPU rows ran about 1.1–1.5× slower than on jax 0.10.2; the flag and the version are not separated.
- Phase 4 measures parallel efficiency; a measured η that reorders the setups supersedes this record.

## History

First designation for this likelihood, regime and hardware class.
