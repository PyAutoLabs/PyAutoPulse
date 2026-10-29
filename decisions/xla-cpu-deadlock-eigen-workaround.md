# Keep --xla_cpu_multi_thread_eigen=false for the 2d JAX CPU legs (jaxlib 0.11.2 deadlock)

Date: 2026-10-29
Decision maker: James Nightingale
Decision source: Human decision in chat on 2026-10-29, verbatim: "keep the workaround which ensures we retain the fastest run times and make sure this knowledge is retained in Pulse for going forward". Recorded as decision D12 on the 2d campaign page in [autolens_profiling#484](https://github.com/PyAutoLabs/autolens_profiling/pull/484).

## Campaign

Likelihood-lifecycle phase 2d
([autolens_profiling#473](https://github.com/PyAutoLabs/autolens_profiling/issues/473)): the
`multi_galaxy/{mge, rectangular, delaunay}` (hst) and `group/{mge, rectangular, delaunay}`
(euclid) cells at the standard size on pin 2026.10.25.1. Its laptop smokes found that every JAX
CPU executable deadlocked on a repeated call under jaxlib 0.11.2. The question was which XLA flag
the JAX CPU legs should compile with.

## Evidence

The full account is the knowledge page
[XLA:CPU deadlock on repeated calls (jaxlib 0.11.2)](../knowledge/xla_cpu_deadlock_jaxlib_0_11_2.md)
and the 2d campaign page's "XLA:CPU deadlock" section at
[`caa46fad`](https://github.com/PyAutoLabs/autolens_profiling/blob/caa46fad/wiki/campaigns/multi_galaxy/likelihood_lifecycle_p2d.md#xlacpu-deadlock-found-in-the-laptop-smokes-avoided-by-d12).
In summary (laptop, 8 cores, local library mains, dense JAX CPU, fp64, steady median per call
after compile):

- With default flags every 2d JAX CPU cell hung after 1 to ~35 calls at 0 % CPU, in
  `CpuPjRtRawLoadedExecutable::Execute` -> `tsl::BlockUntilReady` -> `absl::Mutex` futex wait.
- An exported group MGE prefix-3 function, run in a `python -I` process importing only jax,
  deadlocks at ~call 14 by default and runs 300 calls with either flag below.
- Per call:

| Cell | default | `multi_thread_eigen=false` | `concurrency_optimized_scheduler=false` |
|---|---|---|---|
| group/mge | 0.064 s, then hung | 0.080 s | 0.154 s |
| multi_galaxy/mge | hung | 0.053 s | 0.104 s |
| group/delaunay | hung | 4.57 s | 4.42 s |
| multi_galaxy/rectangular | hung | 2.19 s | 1.90 s |

Untested: RAL (same jaxlib 0.11.2 on the pin), the GPU runtime, and whether the 2a/2b JAX CPU
executables (measured without a flag, and completed) are susceptible.

## Options considered

- **`--xla_cpu_multi_thread_eigen=false`.** About 2x faster than the scheduler flag on the MGE
  cells; within ~15 % on the pixelized cells, where it is the slightly slower one. About +25 %
  against the deadlocking default on group/mge.
- **`--xla_cpu_enable_concurrency_optimized_scheduler=false`.** Also avoids the hang; about 2x
  slower per call on the MGE cells.
- **No flag** with a jaxlib that fixes the fault (none known), or **drop the JAX CPU setups**
  from 2d.

## Decision

Keep `--xla_cpu_multi_thread_eigen=false`, the workaround the 2d driver already applies, for the
2d JAX CPU legs (RAL CPU legs and the A100 node's `jax_cpu_sparse_fp64` leg; inert for GPU
executables). The human chose it as the one that keeps the fastest run times, and asked that the
knowledge be kept in Pulse.

## Implications

- No code changes: the 2d driver
  (`scripts/misc/likelihood_breakdown/galaxy_group_standard.py`, `XLA_CPU_WORKAROUND_FLAG`)
  already appends the flag and records it in each row's `device.xla_flags` and
  `configuration.xla_cpu_workaround`.
- A 2d JAX CPU row is not like-for-like with a 2a/2b JAX CPU row, which ran without the flag.
- This record sets no library or workspace default. PyAutoNerves is unchanged; the per-backend
  question of which XLA flags to set by default stays with task
  [pair_jax_xla_env_vars_with_measured](../tasks/pair_jax_xla_env_vars_with_measured.md).
- Recording the decision submits no compute and gives no batch go.

## Revisit conditions

- A jax / jaxlib version other than 0.11.2: re-run the minimal repro with `XLA_FLAGS` empty; if
  it no longer hangs, dropping the flag is a new decision.
- Evidence from RAL that the default does not hang there, or that the flag costs more than on
  the laptop.
- Evidence that the 2a/2b JAX CPU executables also hang, which would widen the question to them.

## History

First record for this choice (2d decision D12, drafted 2026-10-29, decided the same day).
