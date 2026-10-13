# HST/MGE CPU pilot — collection choices for review

Campaign: setup-baseline
Parent task: [hst_mge_cpu_pilot](hst_mge_cpu_pilot.md)
Prepared: 2026-10-13
Status: proposed choices; no production specification frozen
Preparation issue: [Pulse #58](https://github.com/PyAutoLabs/PyAutoPulse/issues/58)

The human requested continued preparation under `--auto` and explicitly kept
[project correctness audit #417](https://github.com/PyAutoLabs/autolens_profiling/issues/417)
with its current session. This document supplies the Pulse-side collection
choices; it does not replace that audit, implement a witness, approve tolerances
or authorize collection. Earlier approvals of tooling and preparation remain valid.
The existing campaign and task remain the canonical queue; this supporting page
is not a new experiment or an additional task.

## What this pilot would establish

A qualified pilot would measure cold compilation, demonstrated persistent-cache
reuse and steady execution for one fixed-parameter HST/MGE CPU/fp64 objective on
one frozen host/stack/input configuration. It would quantify repeatability within
that configuration, with ten independent cold processes and ten seeded warm
processes. The steady runtime's ten calls occur in one process: they do not
establish between-process runtime variability or general modelling throughput.

The pilot would not establish improvement over historical flat-vector posterior
measurements, which use an incompatible objective. Compilation and execution are
separate costs; the seed cost is retained. A finite output, successful cache hit
or faster timing does not establish scientific correctness or baseline acceptance.

## Verified candidate inputs — not yet selected for collection

Reviewed project revision:
[`e4266a1355a860d2274a82722858349cd3521e46`](https://github.com/PyAutoLabs/autolens_profiling/tree/e4266a1355a860d2274a82722858349cd3521e46).
The local files below match the bytes at that Git revision. Dimensions and BITPIX
were read from the primary FITS headers; values, units, masks, PSF normalization,
noise validity and data origin were not scientifically validated in this step.

| File under `dataset/imaging/hst/` | Header shape (NAXIS2 × NAXIS1) | BITPIX | File bytes | SHA256 |
|---|---|---|---|---|
| [data.fits](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/dataset/imaging/hst/data.fits) | 141 × 141 | -64 | 164160 | `e4e833a28e9c6f6fb023cd85c0d3dde74068720256bc77a240633500e5b04fac` |
| [noise_map.fits](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/dataset/imaging/hst/noise_map.fits) | 141 × 141 | -64 | 164160 | `315c6266a0acd3ac9c8da82fcd2b45a08697362481fd7a35072bab1658530ba3` |
| [psf.fits](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/dataset/imaging/hst/psf.fits) | 21 × 21 | -64 | 8640 | `8389ba0e8bf4a09b4a561cfc246181a2fb944ed396754cd0ff76fdd22910d303` |

These identify the existing candidate reproducibly; they do not prove that it is
observational or simulated, suitable for the scientific question, or the same
bytes as the eventual RAL copy. An instrument label and simulator code nearby
are not origin evidence. Production selection must record origin and reverify
these hashes on the execution host. If observational, inspect contaminants and
agree the mask with the human before collection. Do not simulate replacement
inputs silently.

The [builder](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/scripts/misc/cell_builders/imaging_mge.py)
and [manual workload](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/scripts/misc/jax_compile/current.py)
declare 0.05 arcsec pixels, a 3.5 arcsec circular mask, radial LP oversampling
[4,2,2] at [0.3,0.6], two 20-Gaussian light components, fixed mass/shear and
prior-median free parameters. These source declarations are not an audit of the
actual effective solver settings, input leaf types or masked-pixel count.
Resolving the latter belongs with the project qualification work.

## Verified plan-only capability

The existing [project driver](https://github.com/PyAutoLabs/autolens_profiling/blob/e4266a1355a860d2274a82722858349cd3521e46/scripts/misc/jax_compile/pilot.py)
was invoked without `--run`, using the candidate directory, a new unused output
name inside `output/hst_mge_pilot_v1/`, and one CPU from the local allowed affinity.
It returned a plan successfully, created no output directory and launched no
workers. The local CPU selector only satisfied the planner; it is not a chosen
RAL host or production affinity. No profiling or witness calculation was run.

The plan reports `imaging-mge-runtime-v1`, `accepted: false`, matching input hashes,
31 processes, 1800 seconds per process, 55800 maximum worker seconds, three
runtime warmups and ten runtime samples. Its explicit qualification blockers are:

- Independent scientific correctness reference and reviewed tolerances absent.
- Background load excluding campaign work is not measured.
- Frozen host/stack/dataset/configuration and collection approval not verified.

## Choices to resolve before collection

| Choice | Verified now | Proposal / next decision | Still required |
|---|---|---|---|
| Input dataset | Candidate identities above | Start by qualifying these existing bytes to preserve continuity with the shipped builder; use a different dataset only through an explicit scope decision | Establish origin, suitability, value/PSF/noise checks and execution-host hashes; observational inspection if applicable |
| Hardware | CPU-only; production CPU policy requires `ral` | One named RAL CPU host and fixed core/affinity, one numerical thread, one worker at a time | Actual available node/class, CPU model/topology, affinity, RAM, storage quota and collection window; no allocation requested here |
| Software | Producer implementation pinned above | Select a mutually compatible set of clean full Git SHAs plus a reproducible environment lock on the chosen host | Python/JAX/jaxlib/numerical packages, build flags, OS and all five PyAuto library revisions; a package inventory alone is not a lock |
| Model and solver settings | Builder declarations above | Retain the narrow current-runtime CPU/fp64/jit objective; explicitly capture every effective setting | Project audit of objective normalization, parameter and coefficient ordering, mask/oversampling and actual solver configuration; no defaults changed |
| Correctness | No independent witness or accepted tolerances | Consume the design from #417 before choosing implementation and acceptance rules | Human scientific review of independence, objective parity, absolute/relative bounds and near-zero handling; a separately scoped implementation/execution phase |
| Background load | Runner reports load averages that include its own work | Develop an interval-based method separating campaign CPU activity from other work on the selected allocation, and retain raw counters/time intervals | Validate attribution on that host, including shared-core/SMT activity and scheduler context; the existing proposed ≤0.1 per allocated CPU bound has no accepted measurement method yet |
| Cache evidence | Runner matches target module/key between seed miss and warm hit | Retain isolated cold caches and separate seed/warm pairs, with identical workload/stack/flags | Verify host storage and exact JAX diagnostic compatibility during authorized collection; faster compile alone is insufficient |
| Resource ceiling | Driver caps workers/time; scheduler RAM is external | Keep the existing 32-process / 16 CPU-hour overall draft ceiling, with 16 GiB RAM per process | Human resource approval and scheduler enforcement; correctness process feasibility must fit its separate allowance or the proposal must be revised |
| Collection and acceptance | Neither authorized | Review one complete project specification before requesting a collection window | Explicit compute authorization; independent later scientific acceptance and any baseline promotion |

The background-load row is a method requirement, not a working estimator. Do not
subtract a guessed one CPU from a load average or silently call it background
load. The shipped `--xla_cpu_multi_thread_eigen=false` child setting is part of
the method to freeze and record, not evidence that it is an optimal global flag.
Any changed flag, host, stack, data, model, precision or estimator needs a distinct
configuration identity; it is not a directly comparable before/after result.

## Resource accounting and stop rules

| Leg | Processes | Hard cap per process | Maximum CPU-hours at one allocated CPU |
|---|---:|---:|---:|
| Cold compile | 10 | 1800 s | 5 |
| Cache seed | 10 | 1800 s | 5 |
| Warm compile | 10 | 1800 s | 5 |
| Steady runtime | 1 | 1800 s | 0.5 |
| Independent correctness, reserved but not implemented by this runner | 1 | 1800 s | 0.5 |
| Total proposal | 32 | | 16 |

The shipped runner's portion is 31 processes / 15.5 worker-hours. The overall
16-hour proposal is a worst-case CPU budget, not an expected duration or a
scheduler wall-time estimate: queue time, driver overhead and allocation idle time
can add elapsed time. At a 16 GiB per-process request, the 32-worker cap corresponds
to 256 GiB-hours of worker resource envelope; scheduler billing/reservation can
include extra time. No memory requirement was measured in this preparation.

Stop on timeout, OOM, wrong backend/precision/context, missing input or provenance,
invalid affinity/load evidence, failed correctness, or absent/ambiguous target
cache evidence. Keep failures and missing legs visible. There are no silent retries,
cap increases or GPU fallback. The independent correctness process may need more
than the reserved allowance; #417 must establish feasibility before a final budget.

## Handoff and next bounded action

The correctness session continues #417. Pulse should review its resulting design
alongside this document, resolve the dataset and host/stack choices, and identify
any missing project implementation (witness, resolved-settings capture or load
instrumentation) as bounded Mind tasks. No such implementation is started by this
page. Project repositories own executable specifications, drivers and measurements.

The eventual approval packet should link one immutable project specification,
input/source/config hashes, environment lock, selected hardware/allocation, load
method, correctness design and implementation, tolerance decision and total resource
ceiling. Until these are resolved, collection remains unauthorized and the broader
baseline manifest stays draft. Preparing this page changes neither `last_checkin`
nor measurement freshness and does not create a decision-history entry.
