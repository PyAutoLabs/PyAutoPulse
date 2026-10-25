# Comparing CPU-parallel and GPU-batched setups

Status: knowledge, not a decision. Written 2026-10-25 for likelihood-lifecycle phase 2x
([PyAutoPulse#76](https://github.com/PyAutoLabs/PyAutoPulse/issues/76)). No human decision is
recorded here: which hardware a fit uses is phase 3's decision, made per node and with the
parallel efficiency that phase 4 measures. The autolens_assistant reads the rules below. The
numbers come from autolens_profiling at
[`29caed89`](https://github.com/PyAutoLabs/autolens_profiling/tree/29caed89879399db78f2c6b3734558c844a66b19).

## Why per call is the wrong comparison

Under Nautilus multiprocessing, a numba CPU fit runs one serial likelihood per core, so a CPU node
evaluates many calls side by side. A JAX GPU fit runs one process per GPU and batches points with
`jax.vmap`. On hst Delaunay an A100 call is 27× faster than a numba call, yet the CPU node is projected
to do more calls per second.

**Rule 1.** Never headline GPU vs CPU from per-call latency alone. Compare calls per second per
node, and say that the per-node number is a projection until phase 4 measures it.

## The projection, as the producer declares it

Every runtime record in the lens catalogue carries `resources` and `projected_node_throughput`
([catalogue README](https://github.com/PyAutoLabs/autolens_profiling/blob/29caed89879399db78f2c6b3734558c844a66b19/catalogue/README.md),
autolens_profiling#463 and #465). Pulse validates and displays them. It computes no projection
and issues no verdict.

```
CPU host:  workers = min(floor(cores / cpus_per_eval), floor(memory_gb / peak_rss_gb))
GPU host:  workers = min(gpus, floor(cores / cpus_per_eval), floor(memory_gb / peak_rss_gb))
calls/s per node = workers × η / per-call seconds
```

- The per-call time is numba's warm iid median (`warm_iid_median_s`) or JAX's `vmap` per-call
  time, the batched cost a sampler pays per point.
- `bound_by` names the limit that sets the worker count: `cores`, `memory` or `gpus`.
- **Rule 2.** A row is projected only onto the host class it was measured on: a ral-node row onto
  a ral node, an A100 row onto a gpu node. A per-call time is never carried to another machine.
  Rows from the laptop or from a class with no reference host are `not_projected`, with a reason.

## What the projection does not know

- **η, the parallel efficiency, is declared 1.0 and unmeasured.** It is an upper bound. Hundreds
  of CPU workers share memory bandwidth and caches, so the CPU numbers are the most optimistic.
  **Rule 3.** Treat every per-node number as an upper bound until a phase-4 record replaces the
  declared η with a measured one.
- **Memory caps CPU workers.** Peak RSS is the leg's sacct MaxRSS: exact per leg on RAL CPU, and on
  A100 the multi-leg job's peak, an upper bound. One ao Delaunay numba worker peaks at about 23 GB,
  so a 921 GB ral node fits 40 workers, not 236. **Rule 4.** When `bound_by` is `memory`, the CPU
  node is running most of its cores idle; check peak memory before assuming one worker per core.
- **Is the W̃ operator shared after fork?** Unknown. Forked workers might share the parent's
  precomputed operator through copy-on-write pages, which would lower the real per-worker memory
  and raise the memory cap. The projection assumes no sharing (each worker's own peak RSS).
  Phase 4 measures it.
- **The Nautilus batch ceiling is not modelled.** Nautilus evaluates at most `n_batch` points in
  parallel per batch, so one fit cannot use more workers than `n_batch`. **Rule 5.** For a single
  fit, the usable workers are min(projected workers, `n_batch`); a node projection above
  `n_batch` only pays off when the node runs several fits at once.

## The fork rules

- **JAX never forks.** PyAutoFit refuses to fork a multiprocessing pool for a JAX analysis: a
  forked child of a JAX-initialised process can deadlock in XLA and recompiles the likelihood per
  worker. JAX parallelism comes from the vectorised `jax.vmap` objective
  ([`autofit/non_linear/parallel/pool.py`, `JAX_FORK_REASON`](https://github.com/PyAutoLabs/PyAutoFit/blob/898761b977b78ba4e45e1342cfc79604e6316a7d/autofit/non_linear/parallel/pool.py)).
  JAX must not be initialised before Nautilus forks its workers.
- **numba is imported before the fork.** Importing numba for the first time inside forked workers
  segfaulted Nautilus at 16 or more workers. `Fitness.prepare_for_fork()` now runs the likelihood
  once and imports numba before any likelihood pool forks
  ([PyAutoFit#1715](https://github.com/PyAutoLabs/PyAutoFit/pull/1715)).
- **Rule 6.** A JAX CPU or GPU worker count is a count of independent processes on the node (for
  example several fits at once), never forked workers of one fit. Only numba fits get their
  per-node parallelism from forking.

## RAL reference hosts

From [`catalogue/reference_hosts.json`](https://github.com/PyAutoLabs/autolens_profiling/blob/29caed89879399db78f2c6b3734558c844a66b19/catalogue/reference_hosts.json)
(sinfo, 2026-10-25). The smallest node of each partition is declared.

| Host | Cores | Memory | GPUs | host_class |
|---|---|---|---|---|
| ral node | 236 | 921 GB | 0 | `hpc_ral_cpu` |
| gpu node | 124 | 885 GB | 4× A100 80GB | `hpc_a100` |

## Worked examples (phase 2a, imaging Delaunay)

From the [phase-2a campaign page](https://github.com/PyAutoLabs/autolens_profiling/blob/29caed89879399db78f2c6b3734558c844a66b19/wiki/campaigns/imaging/likelihood_lifecycle_p2a.md#comparing-cpu-and-gpu-setups).
All per-node values are projected with η = 1.0.

| Cell | Setup @ node | Per call | Peak memory per worker | Workers (bound by) | Projected calls/s per node |
|---|---|---|---|---|---|
| hst Delaunay | `numba_cpu_sparse_fp64` @ ral node | 951.7 ms | 0.85 GB | 236 (cores) | ≈248 |
| hst Delaunay | `jax_gpu_dense_fp64` @ gpu node | 35.05 ms | ≤10.7 GB | 4 (GPUs) | ≈114 |
| ao Delaunay | `numba_cpu_sparse_fp64` @ ral node | 8,671 ms | 23.0 GB | 40 (memory) | ≈4.6 |
| ao Delaunay | `jax_gpu_dense_fp64` @ gpu node | 366.93 ms | ≤39.8 GB | 4 (GPUs) | ≈10.9 |

- **hst.** The A100 call is 27× faster, yet a ral node is projected at about twice the A100
  node's calls per second, because 236 numba workers fit in memory.
- **ao.** Each numba worker needs 23 GB, memory caps the ral node at 40 workers, and the 4×A100
  node is projected ahead.

The same likelihood can flip between CPU and GPU with dataset size, through the memory cap.
**Rule 7.** Read `bound_by` along with the throughput: a memory-bound CPU projection is the case
most likely to change when phase 4 measures W̃ sharing and η.

## Where to read the numbers

- The Pulse board's lifecycle setup browser: set **View** to **Per node (projected)**. Each
  projected value has a **projected** badge whose tooltip gives η, its source and the bounding
  limit. The default view stays per call until phase 4.
- The record fields are specified in [REFERENCE.md](../REFERENCE.md), under "Resources and
  projected node throughput".
