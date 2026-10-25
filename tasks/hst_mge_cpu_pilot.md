# HST/MGE fp64 CPU pilot — draft contract

Campaign: setup-baseline
Task: hst_mge_cpu_pilot
Reviewed: 2026-10-13
Status: superseded

The human approved preparation in this chat ("ok go", 2026-10-13). This document
proposes the experiment; it does not freeze a specification or authorize compute,
scientific acceptance, defaults, pins or expansion of the wider baseline matrix.
[Parent task](setup_baseline_campaign.md). Preparation: [Pulse #53](https://github.com/PyAutoLabs/PyAutoPulse/issues/53).

## Question and useful outcome

Can one current HST/MGE likelihood be measured repeatably on a specified RAL CPU,
with auditable cold compilation, persistent-cache reuse and steady execution?
The outcome is a qualified measurement procedure and a first within-configuration
repeatability assessment. There is no compatible before/after baseline yet.
Historical physical-vector posterior timings and this model-instance likelihood
have different objectives; do not calculate a speedup or regression between them.
A faster warm compile alone does not prove a cache hit or scientific correctness.

## Verified capability, reviewed 2026-10-13

[Project #414](https://github.com/PyAutoLabs/autolens_profiling/pull/414) merged at
`b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76`. It supplies an explicit manual path
for imaging/mge/hst, fp64, `jit` only. The global registry still declares the
compile grid unavailable; the profiling conductor emits no dispatch. That global
restriction does not remove the narrow manual builder. No project profile was
run during this preparation, and no HPC state was queried.

The baseline draft validator remains blocked, with 620 unverified, 366 unsupported
and 58 not-applicable slots; specification SHA256:
`468721f7e0e0c0d52957596ddbea964c61273a31d4371b65edeea45858c0a091`.
These are readiness counts, not completed measurements. The 1,044-slot manifest
is unchanged; a pilot never implicitly accepts or removes its remaining slots.

## Workload proposed for the pilot

- Objective: `imaging-mge-runtime-v1`, current `AnalysisImaging` likelihood/figure
  of merit, without external prior or scaling; registered model-instance pytree
  initialized from physical prior medians. Transform `jit`, batch size one.
- Existing HST FITS: `data.fits`, `noise_map.fits`, `psf.fits`. No simulation on
  missing inputs. Pixel scale 0.05 arcsec; circular mask radius 3.5 arcsec;
  radial LP oversampling [4,2,2], radii [0.3,0.6], center (0,0).
- Twenty Gaussian lens-light components and twenty Gaussian source components;
  lens redshift 0.5, source redshift 1.0. Fixed Isothermal mass centered (0,0),
  Einstein radius 1.6, axis ratio 0.9, angle 45 degrees; shear (0.05,0.05).
  Dense MGE inversion; sparse-operator flag false. Actual solver/config defaults
  and model priors must be captured, not reconstructed from this prose.
- CPU backend required and verified at execution, x64 enabled and floating input
  leaves fp64. No gradients, mixed precision, GPU, batching, solver change or
  component breakdown in this first pilot. Host RSS is a resource diagnostic,
  not acceptance of the broad campaign's memory axis.

Dataset bytes, origin (simulated or observational), dimensions, PSF dimensions,
masked-pixel count, resolved full model/solver configuration and every input leaf
remain **unverified for the selected run**. Hash actual inputs and source/config
files. If observational data are chosen, inspect image/contaminants and agree the
mask before use. An instrument name or synthetic development fixture is not the
production dataset identity.

## Proposed measurement protocol

1. Use one fixed named host, CPU model, affinity/core, thread configuration and
   frozen environment across every leg. Capture topology, RAM, OS/kernel, Python,
   JAX/jaxlib, numerical dependencies/build flags, CPU backend, actual process
   affinity and effective thread/XLA/cache settings. Pin clean 40-character SHAs
   for profiling, Nerves, Fit, Array, Galaxy and Lens, and hash an environment
   lock reproducible on that host. The merged builder SHA is an implementation
   reference, not a frozen executable stack.
2. Ten cold compile repetitions: fresh process and fresh empty isolated persistent
   cache per repetition. No pre-call/warmup before trace or compile. Measure
   tracing plus lowering together (label honestly), then AOT compilation, then
   first synchronized execution as three separate intervals. Keep setup and total
   process wall time separately; never add compilation to steady runtime.
3. Ten warm compile repetitions: each has its own separate seed process and a
   matching cache, followed by a fresh measured process. Bind seed/run/cache to
   identical software, flags, workload and input identities. Keep seed cost
   separately. Require positive JAX cache-hit evidence associated with the
   workload executable. File counts and faster timings are insufficient; absent
   or ambiguous hit evidence means unknown cache state, not a warm result.
   Interleave cold and seed/warm groups using a recorded order to expose drift.
4. Separate steady-runtime process: record its setup, compilation and first
   execution separately, then three untimed warmups and ten individual calls.
   Synchronize all outputs before and after each timed call. Retain unrounded raw
   seconds; report median, range and IQR. Ten calls in one process describe
   within-process variability only, not ten independent process replications.
   Retain each cold/warm process sample too; show dispersion and time order,
   without inventing a speedup significance threshold.
5. Collect host load alongside repetitions and the actual affinity/thread state.
   The reference proposal is background load per allocated CPU <=0.1, but its
   method must distinguish other work from this process and account for shared
   host activity. Freeze that method before execution; do not subtract an assumed
   one CPU from load averages. Missing host/load evidence remains unqualified.
6. Correctness: choose an independently computed reference for the identical
   objective, input and reconstruction, preserving reference bytes/hash and
   implementation provenance. An independent NumPy/dense calculation is a
   candidate only after objective/normalization parity is demonstrated. Comparing
   the same JAX function eager versus compiled is a useful consistency test but
   not the independent scientific witness. Human review must fix absolute AND
   relative bounds and near-zero normalization before collection. No numerical
   tolerances or reference are accepted by this draft. Gradients are out of scope.

The current probe rounds samples, reports a three-call steady mean and deliberately
labels configured caches unknown. It is not a baseline-observation producer.
A project-owned runner must implement these missing observations before use;
never convert old probe rows into fresh baseline evidence by relabeling them.

## Proposed resources and stop rules — not a submission authorization

RAL `ral` partition only; one task/process at a time, one allocated CPU with fixed
affinity and one numerical thread; no GPU allocation. Propose 16 GiB RAM per
process, subject to host selection and a reviewed resource preflight. Neither
that memory request nor the duration is an observed requirement.

Hard ceiling: 1,800 seconds per process, including setup. Ten cold + ten seeds +
ten warm + one steady-runtime + one correctness process = at most 32 processes,
16 allocated CPU-hours and 256 GiB-hours at the proposed memory request. Sequential
execution is at most 16 compute wall-hours plus queue/driver overhead. All pilot
work must fit the approved total; extra validation, retries or additional witness
work require a revised budget. Development unit tests are separate from collection.

Stop on timeout, OOM, correctness failure, backend/precision/provenance mismatch,
missing inputs or invalid affinity/load evidence. Preserve logs and incomplete
results; never raise caps, move to GPU or retry silently. Missing cache-hit proof
blocks warm qualification. Caches live under allocated project output on RAL,
never node /tmp or home. Select the exact node class/name, available RAM, storage
quota, load method and collection window before approval; these remain unknown.

## Ownership, deliverables and gates

Pulse retains this intent and the outstanding decisions. The bounded Mind draft
[HST/MGE pilot observations](https://github.com/PyAutoLabs/PyAutoMind/blob/9251122a/draft/feature/autolens_profiling/hst_mge_pilot_observations.md) covers a project-owned
fresh-process runner, raw samples, cache evidence and honest observation output.
The project will own the executable pilot specification, drivers, correctness
artifacts, raw measurements and report. This document is not an executable spec.

Before compute, require: reviewed producer; explicit pilot scope distinct from the
full campaign; immutable project spec and stack/environment lock; named hardware,
affinity and load method; complete hashed dataset/model/solver settings; independent
witness and reviewed tolerances; accepted resource ceiling; collection window and
separate human compute authorization. A partial broader baseline report must
continue showing all missing cells; do not narrow the main manifest silently.

The project report should preserve exclusions and failed/missing observations,
separate integrity from qualification, and remain `accepted: false` pending human
review. Scientific acceptance and any baseline/pin promotion are later decisions.

## Dated source links

Reviewed 2026-10-13 at project merge `b8b3b23`; source review does not refresh measurements:

- [Current workload/provenance](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/scripts/misc/jax_compile/current.py)
- [MGE builder](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/scripts/misc/cell_builders/imaging_mge.py)
- [Probe measurement boundaries](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/scripts/misc/jax_compile/probe.py)
- [Baseline procedure](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/baseline/README.md)
- [Draft baseline manifest](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/baseline/campaign.json)
- [Global route registry](https://github.com/PyAutoLabs/autolens_profiling/blob/b8b3b23cd1f0aabc2d7d4ce1cd297f7420b14f76/catalogue/script_routes.json)


## Implementation handoff — 2026-10-13

Preparation [Pulse #54](https://github.com/PyAutoLabs/PyAutoPulse/pull/54) merged
at `71c93fc285a081ffb1f0f506694c043a15ad4e22`; bounded implementation approved by
the human ("ok continue"). [Project #415](https://github.com/PyAutoLabs/autolens_profiling/issues/415)
owns a separate raw pilot runner: fixed parameters, fresh processes, unrounded
phase timings, target-specific cache diagnostics and actual-context checks.
No inference is performed. The runner's records will remain `accepted: false`;
independent scientific correctness and validated background-load methodology
remain prerequisites for collection qualification, not inferred implementation
successes. The full baseline reader/manifest stays unchanged.

The producer moved to [Mind active work](https://github.com/PyAutoLabs/PyAutoMind/blob/main/active/hst_mge_pilot_observations.md).
Production compute, campaign freeze and scientific acceptance remain unauthorized.


### Development evidence — 2026-10-13

At project commit `b5b8160b23d9a59bb9cb712c1d7bdd35198fbad1`, a local CPU development
fixture (11x11 synthetic image, 3x3 PSF, fp64, one repetition, 60-second per-worker
cap) completed cold, seed, warm and runtime in four distinct processes. The warm
worker reported the target executable's cache hit with the seed's matching key;
the runtime worker retained ten individual synchronized samples. All records
remained `accepted: false`. This verifies producer mechanics only: it supplies no
production timing comparison, independent scientific witness or accepted baseline.
The 32 protocol tests passed and independent code review was CLEAN after rejecting
dirty/unknown source identities. Project #415 retains the implementation and PR
validation record; full scientific qualification remains pending here.

Implementation PR: [autolens_profiling #416](https://github.com/PyAutoLabs/autolens_profiling/pull/416), opened 2026-10-13; pending CI/merge.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. HST/MGE raw fixed-parameter CPU runner merged in #416; Pulse handoff #55 merged and Mind implementation closed. Resolve exact production host/stack/data, full settings, independent correctness witness/tolerances and background-load method. No collection, campaign freeze or acceptance authorized; global compile dispatch remains unavailable.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.


## Collection choices prepared — 2026-10-13

[Collection decision document](hst_mge_cpu_pilot_choices.md) records candidate
FITS identities and the existing driver's plan-only resource bounds, distinguishing
verified facts from unresolved production choices. The human requested this
Pulse-side preparation under `--auto`, leaving the independent correctness audit
[project #417](https://github.com/PyAutoLabs/autolens_profiling/issues/417) with its
current session. No witness or profiling execution, campaign freeze or acceptance
was authorized. This focused preparation does not advance the all-campaign
`last_checkin` or measurement dates.

### Post-/prm 2026-10-17 — qualification design merged

- autolens_profiling#418 merged 2026-10-17 under human `/prm` after an independent review (verdict FINDINGS, none blocking a doc-only merge; review posted on the PR). Issue #417 closed. Mind record: [complete/2026/10/hst-mge-pilot-qualification.md](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/hst-mge-pilot-qualification.md).
- The design (`scripts/misc/jax_compile/QUALIFICATION.md`) derives what the pilot computes, proposes an independent operator + scipy NNLS witness, lists the identities to capture and gives candidate tolerances marked unaccepted. No contradiction with the #416 runner.
- Carried, not fixed: no background-load method proposed; the 1e-8 relative image L2 budget is likely unattainable against the packaged solver's inactive-column flux allowance, so synthetic-harness calibration must be allowed to revise tolerances; correctness-process feasibility is deferred, so the 32-process / 16 CPU-hour budget stays unfinalized. Witness placement in autolens_workspace_test with a project adapter needs the human's confirmation.
- No collection, campaign freeze or acceptance authorized.

## Superseded by phase 2a — 2026-10-25

The human chose to adopt the likelihood-lifecycle phase-2a imaging campaign's MGE/HST
CPU cell as this pilot's answer and close the pilot ("that's what I meant, so do it",
2026-10-25). The pilot's own protocol was **not** run.

- Answering cell: `results/imaging/mge/hst/jax_cpu_dense_fp64/hpc_ral_cpu/runtime.json`
  in autolens_profiling, with `breakdown.json`, `fit.png` and `parity.json` (`match`
  against the eager NumPy reference) beside it. It was measured on RAL `ral` CPU from a
  private checkout at tag 2026.10.23.1 (batch 1 array 412925) and merged in
  [autolens_profiling#461](https://github.com/PyAutoLabs/autolens_profiling/pull/461).
  Campaign issue: [autolens_profiling#456](https://github.com/PyAutoLabs/autolens_profiling/issues/456).
- How it differs from this proposal: the phase-2a cell runs the standard
  production MGE at the instrument's seeded prior draw, not the 20+20 Gaussian fixed
  instance. It records single-jit medians and vmap per-call times, with compile time
  reported separately, not the cold / warm / persistent-cache stages. It applies no
  background-load qualification: the dashboard refuses rows whose load average exceeded 8,
  and the catalogue and coverage still count them. Correctness comes from the
  per-cell parity witness, not the operator + scipy NNLS witness in QUALIFICATION.md.
- The open questions above (persistent-cache auditing, background-load method, tolerance
  calibration) are not answered by this adoption. If they matter again, open a new task;
  do not reissue this pilot.

