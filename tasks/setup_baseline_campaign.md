# Freeze the setup baseline specification, then collect and review evidence

Campaign: setup-baseline
Task: setup_baseline_campaign
Reviewed: 2026-10-06

Current scheduling state lives in `campaigns.yaml`. This is a pending scientific
campaign task, not authorization to run jobs or accept measurements. The project
specification is being implemented under
[autolens_profiling#384](https://github.com/PyAutoLabs/autolens_profiling/issues/384);
those specification changes do not complete baseline collection or scientific
acceptance.

## Project specification and evidence

- [Draft campaign manifest](https://github.com/PyAutoLabs/autolens_profiling/blob/62a6ad1e82735e360c7cf25be62253a286493b17/baseline/campaign.json)
- [Baseline procedure and report contract](https://github.com/PyAutoLabs/autolens_profiling/blob/62a6ad1e82735e360c7cf25be62253a286493b17/baseline/README.md)
- [Project campaign ledger](https://github.com/PyAutoLabs/autolens_profiling/blob/62a6ad1e82735e360c7cf25be62253a286493b17/wiki/campaigns/setup_baseline.md)
- [Compile route capability](https://github.com/PyAutoLabs/autolens_profiling/blob/62a6ad1e82735e360c7cf25be62253a286493b17/catalogue/script_routes.json)
- [Pending compile-builder task](jax_compile_probe_needs_own_cell_builder.md)
- [Measurement noise audit](timing_noise_audit.md)

The specification links pin the reviewed Phase 6 implementation commit. This
is still a draft, not the later frozen campaign. Record the separately reviewed
frozen manifest identity and project revision before collection. Existing archived measurements remain historical context, without
establishing a fresh campaign baseline or a temporal performance trend. Pulse
keeps its existing receipts and snapshots; this task creates no new measurements.

## Human decisions before freezing

1. Choose full immutable revisions for the profiling project and every library,
   and an immutable dependency lock including Python, JAX/jaxlib and numerical
   dependencies. Record how the executable environment reproduces that lock.
2. Specify each selected setup's dataset content hashes and full scientific
   settings, including model, mask/grid, precision, solver, sampling and all
   relevant defaults. Decide which cells and evidence axes are required.
3. Name the exact CPU/GPU hardware and backend, thread allocation, process
   placement and host-load conditions for each collection leg. Production CPU
   arrays must use `--partition=ral` only. GPU collection needs its own explicit
   device/resource allocation and authorization.
4. Fix timing, synchronization, repetition and uncertainty methodology;
   distinguish compile, warm-up and steady runtime, declare cache state, memory
   metric/measurement boundaries and the necessary correctness/parity witnesses.
   Keep time, compile cost, memory and correctness as separate evidence axes.
5. Decide how to handle unavailable capabilities before collection. The compile
   probe's per-cell builder is explicitly unavailable in `catalogue/script_routes.json`.
   Archive coverage does not make the probe runnable. Repair it through its
   separate bounded development task, or record the gap and obtain a human scope
   decision; never mark compile evidence complete from archived records.

## Next bounded steps and acceptance

1. Have the human resolve the choices above in the project's draft manifest and
   procedure, review its validation and record the frozen manifest identity plus
   the immutable project specification revision. Preserve the decisions in the
   project campaign ledger. A draft or a freeze alone authorizes no compute.
2. Request separate human compute authorization for the named cells, resources
   and measurement methods. Then use the project's drivers to collect against
   that frozen specification, preserving result identities, provenance and
   incomplete/invalid evidence. Record actual execution outcomes in the project.
3. Run the project's report against that frozen manifest and collected evidence.
   Treat its output as readiness for human scientific review; report generation
   never promotes a baseline, moves a pin or grants scientific acceptance.
4. Have the human judge the matched evidence and record acceptance, rejection or
   requested follow-up for each selected setup and evidence axis in the project
   ledger. Only then update this pending task from the recorded decision. Any
   later baseline/pin promotion requires its own explicit authorization.

Until those steps are complete, retain `needs-decision`: no campaign is reported
as running or accepted, and specification implementation remains distinct from
the later collection and review deliverables.

## Check-in 2026-10-07

- Specification merged: https://github.com/PyAutoLabs/autolens_profiling/pull/385 (2026-10-06; issue #384 closed 2026-10-06; PyAutoPulse#17 closed 2026-10-06). `baseline/campaign.json` is status draft, version 1, with `baseline/README.md` readiness contract (https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/baseline/campaign.json, https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/setup_baseline.md).
- Six unknowns recorded verbatim: no frozen revisions/env lock; no collection authorization/window; hardware/affinity identity unselected; each cell needs complete settings, input hashes, witness + tolerances; compile per-cell builder unavailable; proposed fp64/mixed coverage is not evidence of support.
- Status stays `needs-decision`: no collection or acceptance authorized; the check-in authorizes none.

## Note 2026-10-08 (from timing_noise_audit fix phase 2)

- When the frozen specification names a reference host and the v2 catalogue starts writing `qualified: true`, reuse autolens_profiling's `build_dashboard.is_reference_host_class` rule (laptop rows never qualify; a missing load average or host is unqualified with a reason) so the v1 and v2 qualification cannot drift apart. Source: autolens_profiling#405.
