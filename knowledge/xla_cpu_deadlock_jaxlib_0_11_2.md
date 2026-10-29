# XLA:CPU deadlock on repeated calls (jaxlib 0.11.2)

Status: knowledge. Written 2026-10-29 for likelihood-lifecycle phase 2d
([autolens_profiling#473](https://github.com/PyAutoLabs/autolens_profiling/issues/473), draft PR
[#484](https://github.com/PyAutoLabs/autolens_profiling/pull/484)). The human's choice of
workaround is recorded separately, in
[decisions/xla-cpu-deadlock-eigen-workaround.md](../decisions/xla-cpu-deadlock-eigen-workaround.md).
Evidence is on the 2d campaign pages at
[`caa46fad`](https://github.com/PyAutoLabs/autolens_profiling/blob/caa46fad/wiki/campaigns/multi_galaxy/likelihood_lifecycle_p2d.md#xlacpu-deadlock-found-in-the-laptop-smokes-avoided-by-d12)
(shared page) and
[`caa46fad`](https://github.com/PyAutoLabs/autolens_profiling/blob/caa46fad/wiki/campaigns/group/likelihood_lifecycle_p2d.md)
(group page). All timings below are from one laptop (8 cores) on the local library mains, not
the pinned release. Pulse records this; it does not apply, detect or enforce a flag.

## Symptom and how to recognise it

- Lowering, compiling and the first call of a jitted likelihood return normally. A later call of
  the **same compiled executable** never returns. Which call hangs varies run to run (seen from
  call 1 to about call 35), so a short smoke (2 steady calls) can pass by luck.
- The process sits at **0 % CPU**. No thread is doing work.
- `faulthandler` puts the Python thread in JAX's `stages.py` `__call__`.
- Native stacks (`py-spy record --native --idle`, started as the parent of the run) show
  `CpuPjRtRawLoadedExecutable::Execute` -> `tsl::BlockUntilReady` -> `absl::Mutex` futex wait.
- CPU backend only. GPU executables were not seen to hang; a GPU analogue was not tested.

A run that sits at 0 % CPU inside a compiled call is this hang, not a slow compile and not a slow
likelihood. Do not raise a wall time for it.

## Where it was seen

jax / jaxlib **0.11.2**, XLA:CPU. It hit every 2d (`multi_galaxy` + `group`) JAX CPU cell run on
the laptop: MGE, rectangular and Delaunay, dense and sparse. Prefix bisection over the breakdown
stages: group MGE hangs from prefix 3 (data vector) on, group Delaunay from prefix 4 (curvature
matrix); prefixes 1-2 ran 300 calls.

Ruled out: the persistent compilation cache (hangs with `JAX_ENABLE_COMPILATION_CACHE=false`),
BLAS threads (`OPENBLAS/OMP/MKL_NUM_THREADS=1`), the Delaunay `pure_callback` (the MGE cells have
no host callback and hang too), the flat-pytree-leaves driver change, the `dPIEMassSph` mass
(multi_galaxy has none and hangs), and `--xla_disable_hlo_passes=constant_folding` (hangs without
it). A plain jitted `A.T @ A` at the cell's size (17,692 x 1,300), with or without a scipy
`pure_callback`, ran 30 calls fine.

## Minimal reproduction (no PyAuto code in the process)

1. In the cell's own process, build the group MGE cell, take iid draw 0, flatten the instance to
   its pytree leaves, and `jax.jit` the breakdown's prefix-3 function (params -> data vector).
   Export it: `jax.export.export(jf)(params)`, then pickle `exp.serialize()` together with the
   leaves as NumPy arrays. (The 2d driver's helpers are `_jax_cell`, `_flat_params` and
   `_stage_value` in `scripts/misc/likelihood_breakdown/galaxy_group_standard.py`.)
2. In a fresh `python -I` process that imports **only jax**:

```python
import pickle
import sys

import jax

jax.config.update("jax_enable_x64", True)
d = pickle.load(open(sys.argv[1], "rb"))
exp = jax.export.deserialize(d["exp"])
params = [jax.numpy.asarray(p) for p in d["params"]]
c = jax.jit(exp.call).lower(params).compile()
for i in range(300):
    c(params).block_until_ready()  # with a faulthandler timeout around each call
```

With `XLA_FLAGS` empty it deadlocks at about call 14. With either flag below it runs all 300
calls. The exported module (about 3 MB) is evidence for an upstream JAX issue; it is not
committed to any repo.

## The two flags that avoid it

Either flag appended to `XLA_FLAGS` before the JAX backend starts avoids the hang:

- `--xla_cpu_multi_thread_eigen=false`: Eigen ops inside an XLA:CPU thunk run single-threaded.
- `--xla_cpu_enable_concurrency_optimized_scheduler=false`: XLA:CPU uses its default thunk
  schedule instead of the concurrency-optimized one.

So the fault sits in the interplay of multi-threaded Eigen ops and the concurrency-optimized
schedule in XLA:CPU. Neither flag changes what the likelihood computes (every 2d smoke kept
parity `match`); both change how fast it runs.

Steady median per call, full pipelines, laptop, dense JAX CPU:

| Cell | default flags | `multi_thread_eigen=false` | `concurrency_optimized_scheduler=false` |
|---|---|---|---|
| group/mge | 0.064 s, then hung after 35 calls | 0.080 s (150/150) | 0.154 s (150/150) |
| multi_galaxy/mge | hung after 1 call | 0.053 s (40/40) | 0.104 s (40/40) |
| group/delaunay | hung after 1 call | 4.57 s (15/15) | 4.42 s (15/15) |
| multi_galaxy/rectangular | hung after 1 call | 2.19 s (15/15) | 1.90 s (15/15) |

On the MGE cells `multi_thread_eigen=false` is about 2x faster than the scheduler flag. On the
pixelized cells the two are within about 15 %, and the scheduler flag is the slightly faster one
there. Against the deadlocking default (measured only on group/mge, before it hung),
`multi_thread_eigen=false` costs about 25 % per call.

## The decision

The human chose `--xla_cpu_multi_thread_eigen=false` on 2026-10-29: "keep the workaround which
ensures we retain the fastest run times and make sure this knowledge is retained in Pulse for
going forward". The record, its scope and its revisit conditions are in
[decisions/xla-cpu-deadlock-eigen-workaround.md](../decisions/xla-cpu-deadlock-eigen-workaround.md)
(2d decision D12).

## Reading rows measured with the flag

- A row whose JAX leg ran with the flag records it in `device.xla_flags` and in
  `configuration.xla_cpu_workaround` (the 2d driver writes both).
- Such a row is **not like-for-like** with a row measured without the flag: the flag is a compile
  option that changes per-call cost. The 2a (imaging) and 2b (interferometer) JAX CPU rows were
  measured without it. Comparing a 2d JAX CPU row with a 2a/2b JAX CPU row mixes the setup cost
  with the flag's cost (about +25 % on group/mge, the one cell where a no-flag time exists).
- Read the two fields before pairing JAX CPU rows. Pulse displays them; it does not refuse or
  adjust a pairing because of them, and it does not infer the flag from timings.

## Open questions

- **RAL.** The pin 2026.10.25.1 runs the same jaxlib 0.11.2 on RAL (its 2026.10.17.1
  `hpc_ral_cpu` rows record jaxlib 0.11.2). Whether the deadlock fires on a 236-core RAL node is
  untested. The 2d legs apply the flag there regardless.
- **The 2a / 2b JAX CPU cells.** They were measured without the flag and completed. Nobody has
  tested whether those executables are susceptible on repeated calls, or whether a longer run
  (a fit) would hang.
- **GPU.** The flag is inert for a GPU executable; whether the GPU runtime has an analogue was
  not tested.
- **When to re-test and drop the flag.** Any jax / jaxlib upgrade away from 0.11.2 (a new
  release pin or a change to the PyAutoNerves jax bounds) should trigger the minimal repro
  above with `XLA_FLAGS` empty. If it runs 300 calls, the next campaign may propose dropping the
  flag; that is a new human decision, recorded with a "Supersedes" link.
- **Relation to the August Eigen-pool deadlock.** PyAutoMind
  `complete/2026/08/xla-cpu-eigen-pool-deadlock.md` (an `FftThunk` handing ducc0 the Eigen pool)
  was avoided by the same `--xla_cpu_multi_thread_eigen=false` flag, which the test workspaces
  set in CI only. Whether the 2d hang is the same fault is not established; its stack shows no
  thread working. The broader per-backend measurement of XLA flags is task
  [pair_jax_xla_env_vars_with_measured](../tasks/pair_jax_xla_env_vars_with_measured.md).

## Links

- autolens_profiling draft PR [#484](https://github.com/PyAutoLabs/autolens_profiling/pull/484)
  (branch `feature/likelihood-lifecycle-p2d-galaxy-group`), issue
  [#473](https://github.com/PyAutoLabs/autolens_profiling/issues/473).
- 2d shared campaign page (D12 and the "XLA:CPU deadlock" section):
  [`wiki/campaigns/multi_galaxy/likelihood_lifecycle_p2d.md`](https://github.com/PyAutoLabs/autolens_profiling/blob/feature/likelihood-lifecycle-p2d-galaxy-group/wiki/campaigns/multi_galaxy/likelihood_lifecycle_p2d.md).
- 2d group page:
  [`wiki/campaigns/group/likelihood_lifecycle_p2d.md`](https://github.com/PyAutoLabs/autolens_profiling/blob/feature/likelihood-lifecycle-p2d-galaxy-group/wiki/campaigns/group/likelihood_lifecycle_p2d.md).
- The driver that applies the flag (`XLA_CPU_WORKAROUND_FLAG`, `_avoid_xla_cpu_deadlock`):
  [`scripts/misc/likelihood_breakdown/galaxy_group_standard.py` at `caa46fad`](https://github.com/PyAutoLabs/autolens_profiling/blob/caa46fad/scripts/misc/likelihood_breakdown/galaxy_group_standard.py).
