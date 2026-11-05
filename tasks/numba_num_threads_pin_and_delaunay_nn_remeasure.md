Filed: 2026-11-05 (human request in chat: "yes file the profiling follow-up in Pulse")

# Pin `NUMBA_NUM_THREADS=1` in profiling cells and re-measure the DelaunayNN numba Optimal cell after PyAutoArray#677 is released

Type: feature
Target: autolens_profiling
Repos:
- @autolens_profiling
- @PyAutoPulse
Themes:
- numba-cpu
- profiling
Difficulty: small
Priority: medium

## Finding

`autolens_profiling/_production_config.pin_thread_env` pins `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`OMP_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS` and `NUMEXPR_NUM_THREADS` to 1, but **not `NUMBA_NUM_THREADS`**.
numba ignores `OMP_NUM_THREADS`. On the laptop (numba 0.68.1, omp layer), `OMP_NUM_THREADS=1` still gave
`numba.get_num_threads() == 8` and about 5× CPU per wall-second. numba's default is the node's
`cpu_count` (252 on RAL); the SLURM cgroup bounds it to the job's CPUs.

Until PyAutoArray#677 (merged 2026-11-05, pending release) the Sibson interpolator was always a numba
`parallel=True` kernel. So the day-zero cell
`imaging/delaunay_nn/hst numba_cpu_sparse_fp64@hpc_ral_cpu` (class `optimal`, in
`snapshots/day_zero/lens.json`; runtime `warm_iid_median_s` 1.295 s, breakdown per call 1.385 s; RAL job
412955, an 8-CPU array task) ran its Sibson step on up to 8 cores. In production every Nautilus worker is
one process on one core, and since #677 a worker always runs the serial Sibson build, so the profiled
number is optimistic.

Size (laptop, Sibson kernel only, 1,280 vertices × 61,600 over-sampled queries, the profiled HST size):
8 threads 14.1 ms, 4 threads 17.1 ms, 1 thread 56.3 ms. That is about +42 ms per likelihood call for one
interpolation, roughly 3% of the profiled call. RAL cores are slower and a call may interpolate more than
once, so the estimate is 3–10%. That is not enough to reorder setups, but the Optimal row should be the
single-core number.

Not affected:
- every other numba cell: all other numba kernels are serial by default (`general.yaml numba: parallel: false`);
- the interferometer `direct_conv` cells: `parallel: false`;
- the `misc/streaming_scaling` study, which varies threads deliberately;
- the fixed-light breakdown submits, which already export `NUMBA_NUM_THREADS=1`;
- the `delaunay-nn-cpu` campaign measurements (PyAutoArray#637), which were 1-thread.

## Steps

1. **Pin (now, no compute):** add `NUMBA_NUM_THREADS` to `_production_config.THREAD_ENV_VARS`, so
   `configuration.thread_env` records it. It must be set before numba is imported. Cells call
   `pin_thread_env` above `import numpy`, so check that numba isn't imported earlier.
2. **Re-measure after the release carrying PyAutoArray#677:** the DelaunayNN numba runtime + breakdown cell
   on `hpc_ral_cpu` (human go for the RAL job). Mark the 2026.10.25.1 rows `superseded` and keep them.
3. **Pulse:** decide with the human whether the new row replaces the day-zero designation for that cell (a
   day-zero re-freeze of one cell) or stands as a post-day-zero current record. Record the decision.
4. Phase-4 cross-check: the autolens_inference validation leg (RAL 414189, pin + #677) measures wall
   time with serial Sibson in workers. Its implied per-call can be compared with the step-2 row.

## Evidence

- Failure and fix: PyAutoArray#676 / #677 (numba `prange` kernels serial in multiprocessing workers);
  Mind record `complete/2026/11/numba-fork-safe-threading.md`.
- Row provenance: `results/imaging/delaunay_nn/hst/numba_cpu_sparse_fp64/hpc_ral_cpu/breakdown.json`
  (`configuration.thread_env.vars` lacks `NUMBA_NUM_THREADS`; `device.cpu_count` 252).
- Human doctrine: numba CPU cost is per process and per core ("one process per core under Nautilus"),
  and numba parallel threads never run inside multiprocessing workers (2026-11-05).
