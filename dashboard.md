# PyAutoPulse — profiling dashboard

<!-- pulse-campaigns:3283e557de1d110da97abe4c9ffeaed914e3a35fa18b55feff3e32ebb760654d -->
## Profiling Check In

<details><summary>Full check-in prompt</summary>

```text
Use PyAutoPulse as the home for profiling work in this ongoing chat. Read PyAutoPulse/AGENTS.md and CHECKIN.md, then the campaign ledger, relevant tasks and registered project evidence. Use Brain’s profiling conductor for profiling analysis and planning, and project-owned drivers for execution.

When I give no particular direction, review every open campaign and task for changes since the last check-in: measurements, jobs, PRs, releases, blockers and recorded next steps. Give me a concise campaign-by-campaign summary and a proposed priority order. Distinguish verified updates from stale, missing or unavailable evidence.

When I name a campaign, measurement, slowdown or idea, make that the main focus. Help me understand a timing result, investigate a regression, compare compatible measurements, identify missing evidence, design an experiment or develop a new campaign. Bring in related work where it affects the question; do not repeat the full campaign review on every follow-up.

Make comparisons explicit about hardware, software versions, datasets, model configuration, precision and measurement method. Keep compilation and execution costs separate. Identify incompatible or incomplete comparisons rather than presenting them as evidence of improvement or regression.

Discuss proposed experiments with me, explaining what each would establish and the resources it needs. Help turn agreed direction into concrete campaign tasks. Keep profiling intent and pending domain work in Pulse, execution and measurements in the project repositories, and bounded implementation work in Mind.

Update the Pulse ledger with verified facts and dated source links, regenerate the board and persist changes through the repository workflow. Keep review dates separate from measurement freshness. Do not infer campaign completion or scientific acceptance from a successful job or a faster timing alone.

Carry clearly authorized work through the appropriate procedure, retaining decisions and approvals already given in this conversation. Launch compute or change defaults, baselines or campaign direction only when authorized; a general check-in does not authorize those actions.

After taking action, report what changed, what the evidence supports and what remains unresolved. Continue subsequent profiling work in this chat and stop at the session deliverable without scheduling background follow-up.
```

</details>

Last check-in: 2026-10-23T15:00:32Z (review date, not measurement freshness).

## Active campaigns

<details><summary>Setup baseline collection and scientific acceptance — needs-decision</summary>

Reviewed 2026-10-17. Review the Pulse collection choices (candidate input hashes and 31-worker resource plan verified without execution) alongside project correctness audit #417. Resolve data origin/suitability, named host/stack/full settings, witness/tolerances and background-load method. No freeze, compute or acceptance authorized. Check-in 2026-10-17: no project wiki/results/issue change since 2026-10-13 beyond autolens_profiling#420/#422/#424 (interferometer only); releases 2026.10.16.1/.2 and 2026.10.17.1 supply no new measurement. Post-/prm 2026-10-17: autolens_profiling#418 (pilot qualification design) merged after an independent review (FINDINGS, none blocking); issue #417 closed; Mind record complete/2026/10/hst-mge-pilot-qualification.md. Carried to the next bounded step: background-load method (none proposed), the 1e-8 relative image L2 budget (likely unattainable; synthetic-harness calibration must be allowed to revise tolerances), and the correctness-process feasibility needed before the 32-process budget is final.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/pull/416)

### Active tasks

- [Freeze the setup baseline specification, then collect and review evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/setup_baseline_campaign.md) — needs-decision: HST/MGE raw fixed-parameter CPU runner merged in #416; Pulse handoff #55 merged and Mind implementation closed. Resolve exact production host/stack/data, full settings, independent correctness witness/tolerances and background-load method. No collection, campaign freeze or acceptance authorized; global compile dispatch remains unavailable.

</details>

<details><summary>Point-source image plane · CPU — active</summary>

Reviewed 2026-10-17. No new committed campaign measurements. Phases 1–4 remain shipped; epic closure is a human decision. Carried leftovers remain pending. RAL queue empty at review, but transfer preview timed out: cleanup folders and unpulled results unverified. Select one owed cleanup/measurement phase only after review. Check-in 2026-10-17: no project wiki/results/issue change since 2026-10-13 beyond autolens_profiling#420/#422/#424 (interferometer only); releases 2026.10.16.1/.2 and 2026.10.17.1 supply no new measurement. RAL queue holds only euclid_dr1 jobs; cleanup folders and unpulled results still unverified.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/results/notes/point_source_cpu_campaign.md#campaign-completion-evidence-2026-10-04)

### Active tasks

- [Point-source (single-source) CPU campaign — carried leftovers and completion evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pointsolver_cpu_speed_campaign_remainder.md) — ready: No new committed campaign measurements. Phases 1–4 remain shipped; epic closure is a human decision. Carried leftovers remain pending. RAL queue empty at review, but transfer preview timed out: cleanup folders and unpulled results unverified. Select one owed cleanup/measurement phase only after review.

</details>

<details><summary>Point-source image plane · A100 — parked</summary>

Reviewed 2026-10-17. Parked as research, human decision 2026-10-17 (chat) (&quot;just research to file&quot;). Reference measurement autolens_profiling#434 (issue #427 closed) merged 2026-10-17 (human /prm): job 412519 euclid-ral-gpu-2 exclusive A100, jax 0.10.2, fp64, 2026.10.17.1 private clone: single call 0.934 ms (pre-#768 0.910), vmap-256 0.0125 ms (0.0120), compile 6.54 s; forward gradient finite 16/16, equal to reverse to 1.6e-11; logL bit-exact; +2.7% not attributed (different node/date). A100 per-step breakdown rows unusable. Phase-2 inference fit measurement dropped; no baseline admitted. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/point-source-image-gpu-admission.md.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/point_source_gpu_breakdown.md)

### Active tasks

- [Point-source A100 speed-up campaign: profile and optimize with the shared breakdown](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_image_plane_gpu_breakdown.md) — parked: Parked, human decision 2026-10-17 (chat). Reference A100 measurement autolens_profiling#434 (merged 2026-10-17 (human /prm), issue #427 closed, job 412519): 0.934 ms single call, 0.0125 ms at vmap-256, forward gradient fixed; phase-2 inference fit measurement dropped. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/point-source-image-gpu-admission.md.

</details>

<details><summary>Cluster PointSolver robustness and performance — active</summary>

Reviewed 2026-10-23. Human decision 2026-10-23 (chat): keep the 1.0″ starting grid as the production default (decision record cluster-pointsolver-starting-grid; closes the phase-1 deferral). Inputs: phase-1 simple sweep (#438), A2744 pilot job 412573 (1.0″ misses fewest, 2/69), starting-grid follow-up autolens_profiling#439 → #440 merged 03d36c81 (no fixed scale finds every image; no separation rule). Mitigation: the workspace validation check. Next bounded task: spurious-core candidates library task (start_dev in progress), then the validation check. No default changed.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/03d36c810b2a4f7d31342d9a75f46cd7fe10f43a/results/notes/cluster_pointsolver_campaign.md)

### Active tasks

- [Cluster PointSolver — robustness, analysis settings and performance](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/cluster_pointsolver_speed.md) — active: Decision taken 2026-10-23 (human): keep 1.0″ + validation check; #439/#440 merged (03d36c81). Next: spurious-core candidates library task (start_dev in progress), then the workspace validation check.
- [PointSolver profiling cells: lensed quasar → cluster runtime tier → single/multi-source → multiplane](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_solver_profiling_cells.md) — ready: Unissued, no claim. Candidate first cell: a representative-data cluster likelihood_runtime baseline (single-source preset). Reconcile onto the phase-1 harness (scripts/cluster/image_plane/robust_settings_sweep.py) when the next cell is issued; no duplicate cell.

</details>

<details><summary>Interferometer likelihood and streaming — parked</summary>

Reviewed 2026-10-17. Evening 2026-10-17: human decision 2026-10-17 (chat): interferometer CPU work is exhaustive and closed; curvature preload parked (&quot;we will come back to it soon&quot;); GPU levers &quot;file wiki research but not make source code changes for now&quot;, so no library prompt for JAX FFT pruning. Parked at knowledge-complete. All merged 2026-10-17 (human /prm), pending release for the library PRs: L2 symmetric direct_conv PyAutoArray#636 (issue #635 closed, pending-release; real Aris RAL 1.49×/1.53×/1.58× at 1,459/2,577/5,746 vertices, logL to round-off; decision record direct-conv-symmetric-gate) + record autolens_profiling#425; A100 FFT levers #433 (issue #429 closed) (pruned FFT 1.08×/1.18×/1.41× whole likelihood at alma/alma_high/jvla; pixel-scale coarsening fails the 0.5-nat bar); streaming 1e8 CPU/A100 + memo after-measurement #435 (issues #368, #426 closed). Route-constant refit (RAL FFT/full direct_conv 0.68 vs 0.89 predicted) deferred. Merged in order #636, #425, #432, #431, #433, #434, #435. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/direct-conv-symmetric.md, https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/ral-route-constants-fft-levers.md, https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/interferometer-streaming-memo-after.md.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/fd29902bd09f/wiki/campaigns/interferometer_likelihood.md)

### Active tasks

- [Interferometer fixed-mapper searches: reuse the W~ curvature matrix across likelihood calls via `preloads.curvature_matrix`](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_fixed_mapper_curvature_preload.md) — parked: Parked, human decision 2026-10-17 (chat): interferometer CPU work closed; &quot;we will come back to it soon&quot;. Phase-1 Mind draft unstarted.
- [fnnls warm-start memo: stop it slowing scattered evaluation streams (interferometer CPU, autolens_profiling#332)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_nnls_memo_scattered_stream_guard.md) — parked: After-measurement autolens_profiling#435 merged 2026-10-17 (human /prm) (issue #426 closed; job 412526, ral compute-10-2, load ~10, 1 thread, 6 rounds, paired bootstrap 90% CI): Delaunay iid #332 flags 1.918 [1.887,1.925] (2.17 in #332); 15 timed solves 1.018 [1.013,1.023]; Delaunay walk 0.46; rect iid 0.887/0.987; rect walk 0.15; FoM identical. Not evidence #613 is fixed. Research owed: Nautilus-replay witness, varied-seed rounds. Parked, human decision 2026-10-17 (chat). Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/interferometer-streaming-memo-after.md.
- [Campaign: interferometer streaming (array-free) vs in-memory — memory and time scaling to 2e8 visibilities](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_streaming_scaling.md) — parked: Phase 2 autolens_profiling#435 merged 2026-10-17 (human /prm) (issue #368 closed): from_stream chunk 65536 fp64, 1e8 vis RAL CPU 707.5 s / 1.78 GB RSS, A100 157.3 s / 1.48 GB device; compile ~3 s constant. In-memory fails at 2.5e5 (RAL 10 GB cap) and 4e6 (A100); uncapped CPU ~7.5 kB/vis. Optional 2e8 rows are research; library candidate (chunk transformer.image_from) unfiled per human decision 2026-10-17 (chat). Parked. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/interferometer-streaming-memo-after.md.
- [Interferometer large-mask likelihood (Aris 512×512): sparse data-vector memory, AdaptSplit log-det backend parity, numba route-gate cost model](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_large_mask_aris.md) — active: L2 shipped to PR: PyAutoArray#636 (head 62a1e3ac, pending-release) + autolens_profiling#425 (results note), both merged 2026-10-17 (human /prm); issue #635 closed. RAL real-data witness 1.49×/1.53×/1.58× at 1,459/2,577/5,746 vertices (pred 1.48×/1.50×/1.53×), logL to round-off; peak RSS 43 GB without NUFFT chunking. Decision record direct-conv-symmetric-gate added. Route-constant refit (0.68 measured vs 0.89 predicted) deferred: CPU lane closed, human decision 2026-10-17 (chat). Remaining: release of #636; shadow row owed in Mind autonomy_log (glance tier; human to confirm merged-unchanged). Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/direct-conv-symmetric.md. Shadow row appended 2026-10-17 (merged-unchanged, stage 1). Human decision 2026-10-17: remaining Aris levers stay research; not enough return to implement for now.
- [Interferometer W~ curvature matrix is FFT-bound on the mask extent: pruned padded FFT and real-space pixel scale on the A100](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_w_tilde_fft_size_levers.md) — parked: A100 research autolens_profiling#433 merged 2026-10-17 (human /prm) (issue #429 closed; job 412515): pruned padded FFT 1.08×/1.18×/1.41× whole likelihood at alma/alma_high/jvla, F exact to 1.7e-15; pixel-scale coarsening shifts log evidence by +1,310 to +2,757 nats (fails). No library prompt, human decision 2026-10-17 (chat). Parked. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/ral-route-constants-fft-levers.md.

</details>

<details><summary>Linear-solver accuracy and cost — active</summary>

Reviewed 2026-10-17. Retain the 2026-10-08 human decision: Jacobi for Mapper, raw+polish for MGE-only, no default change. Project wiki still says decision pending (stale). No new solver measurements after the recorded phase-5 results; release 2026.10.12.1 does not supply a rerun. Wide-prior/interferometer gaps remain evidence gaps, not authorized tasks. Check-in 2026-10-17: no project wiki/results/issue change since 2026-10-13 beyond autolens_profiling#420/#422/#424 (interferometer only); releases 2026.10.16.1/.2 and 2026.10.17.1 supply no new measurement.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md)

### Active tasks


</details>

<details><summary>Production imaging and likelihood breakdown — active</summary>

Reviewed 2026-10-17. Production over-sampling phase 1 merged 2026-10-17 (human /prm): autolens_profiling#431 (issue #430 closed, CPU smoke 8/8): --over-sampling {flat1,production} on the 4 JAX Delaunay/DelaunayNN cells, euclid/hst presets. Findings: HST flat-1 adapt_split pin fails on unmodified main (29155.000 vs 29140.296); numba cells&#x27; production threshold never reaches sub 4 for HST; rectangular JAX cells uncovered. Phase 2 (A100 production re-measure) needs-decision (human decision 2026-10-17 (chat): undecided). DelaunayNN imaging moved to the parked delaunay-nn-cpu campaign. Post-certified, quick-update plotting and other tasks unchanged. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/imaging-production-over-sampling.md. Human decision 2026-10-17 (chat): hold off on phase 2 (A100 production over-sampling re-measure); not authorized, revisit when production imaging needs a cost picture.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/post_certified_breakdown.md)

### Active tasks

- [Profile imaging pixelizations at production over-sampling](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/imaging_production_over_sampling.md) — parked: Phase 1 merged 2026-10-17 (human /prm): autolens_profiling#431 (issue #430 closed, CPU smoke 8/8). Phase 2 A100 production re-measure needs-decision (human decision 2026-10-17 (chat): undecided); requires compute authorization (#431 now merged). Findings: HST flat-1 adapt_split pin fails on main; numba HST threshold never reaches sub 4; rectangular JAX cells uncovered. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/imaging-production-over-sampling.md. Human decision 2026-10-17 (chat): phase 2 A100 re-measure held; task stays parked at phase 1 shipped (#431).
- [Assess remaining likelihood bottlenecks after certified solver integration on CPU and GPUs](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/post_certified_solver_likelihood_breakdown.md) — needs-slicing: Blocked-by is stale: resolved 2026-09-27 (PyAutoArray#567 in 2026.9.26.1). Unissued; scope one bounded phase from the full task contract.
- [Quick-update plotting cost — minutes per update, and it is not JAX compile](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/quick_update_plotting_cost.md) — ready: Unchanged; targets PyAutoLens/PyAutoGalaxy (PyAutoLens#680 closed 2026-07-31, no follow-up issue). Select one bounded step when prioritised.

</details>

<details><summary>DelaunayNN (Sibson) mesh at Delaunay cost on the numba/NumPy CPU path — parked</summary>

Reviewed 2026-10-17. Created parked, human decision 2026-10-17 (chat): &quot;file in research to come back to in the future&quot;. PyAutoArray#637 (issue #629 closed) merged 2026-10-17 (human /prm), pending-release: RAL compute-10-4 exclusive 1 thread A-B-B-A ×2, 1,030 vertices / 15,380 px: NN sub4 0.569→0.392 s (2.20× Delaunay, was 3.00×), sub2 0.235→0.189 s (1.75×); logL bit-identical; fixes the size-0 Sibson NaN case. ~1.5× target not met; remaining cost is Sibson (~0.16 s) + wider curvature rows. Target and two hazards recorded as future work, not filed. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/delaunaynn-wide-row-overhead.md.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoArray/pull/637)

### Active tasks

- [DelaunayNN (Sibson) imaging likelihood at close to Delaunay cost on the numba/NumPy CPU path](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/delaunay_nn_cpu_imaging.md) — parked: Parked, human decision 2026-10-17 (chat). PyAutoArray#637 merged 2026-10-17 (human /prm) (issue #629 closed, pending-release): sub4 2.20× Delaunay (was 3.00×), sub2 1.75×; logL bit-identical. Future (unfiled): ~1.5× target; hazards sub_slim_indexes_for_pix_index padding and Sibson rows with mid-row gaps. Records: https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/delaunaynn-wide-row-overhead.md.

</details>

<details><summary>Measurement reliability and profiling tools — active</summary>

Reviewed 2026-10-17. Timing audit #410–#412 and raw HST/MGE pilot producer #416 merged; implementation issues #362/#415 closed. No fresh production measurements or scientific acceptance. C1/C11 repeat counts, C5 estimator policy, memo interpretation, fresh runtime repeats and other tools remain pending. #418 and #417 open. Evening 2026-10-17 merge-order note: Six open autolens_profiling PRs (#425, #431, #432, #433, #434, #435) all regenerate the shared catalogue/dashboard: each merge after the first needs a rebase + re-render; suggested order #425, #432, #431, #433, #434, #435. #425 after PyAutoArray#636.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/pull/416)

### Active tasks

- [MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/mge_likelihood_breakdown_steps_are_cumulative_an.md) — ready: Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.
- [A gradient-cost probe: forward vs `value_and_grad` ms/eval and a strict FD check, on any registry cell](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_cost_probe.md) — ready: Unissued. New context 2026-10-07: Heart unit-test timing flagged PyAutoLens forward-gradient tests +150%/+96% after PyAutoLens#768 rewrote that test file; not a controlled comparison, and this probe is the right instrument. Select one bounded step when prioritised.
- [Numba breakdown harness: perturb the instance so the operated-matrix memo cannot hide a step](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/numba_breakdown_harness_memo_blind.md) — ready: Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.
- [Search settings-estimation + profiling infrastructure (n_starts / batch_size / n_batch)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/search_settings_estimation_infrastructure.md) — ready: Unchanged and unissued (autolens_profiling#82 closed 2026-08-18). Select one bounded step when prioritised.
- [jax_compile/probe.py lost its cell builder with the searches tier — give profiling its own](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/jax_compile_probe_needs_own_cell_builder.md) — active: Manual HST/MGE fp64 jit builder #414 and separate raw pilot runner #416 merged. Bounded Mind implementations complete; wider builder coverage/global compile dispatch still unavailable. Agree a next capability or separately authorize a qualified pilot; no production compute authorized. Check-in 2026-10-17: autolens_profiling#418 (pilot qualification design) open since 2026-10-13 with CI green and no review; #417 open; no new measurements.
- [profile_lens_aggregator.py cannot run from the autolens_workspace_developer root: no config/ directory](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/profile_lens_aggregator_needs_config_dir.md) — ready: Unchanged: workspace_developer main still has no root config/ (bug presumed live, not re-run). Select one bounded step when prioritised.
- [jax_profiling/gradient/imaging/pixelization.py: 3.2% of its pin move is unattributed](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_pixelization_pin_residual_drift.md) — ready: Unchanged and unissued (PyAutoArray#490 merged 2026-08-26). Select one bounded step when prioritised.
- [Pair JAX/XLA env vars with measured compile and run times, per backend](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pair_jax_xla_env_vars_with_measured.md) — ready: Unchanged and unissued. Context: the jax-version policy is now released (2026.10.7.1 libraries require Nerves with the JAX deadlock exclusions). Select one bounded step when prioritised.

</details>

<details><summary>PyAutoFit profiling bootstrap — active</summary>

Reviewed 2026-10-17. B4a (autofit_profiling#3) and B4b (autofit_profiling#5, issue #4 closed, merged 2026-10-15) shipped: search.fit breakdown cell, profiling-summary@2 exporter, EP/graphical N3/N10/N30 baselines and analytic parity cell; #6 repointed RAL paths to the category layout (2026-10-15). Pulse fit fixture/campaign merged (#60, #61); fit receipt ok at autofit_profiling 58e56b9 (31 records, fetched 2026-10-15T22:58Z), so the post-deploy refresh is done. Epic 2 not opened: next bounded step is a human-scoped epic-2 campaign row; B5c inference work belongs to Insight, not Pulse.

[Campaign evidence](https://github.com/PyAutoLabs/autofit_profiling/issues/4)

### Active tasks

- [autofit_profiling: bootstrap the repo + general PyAutoFit profiling epic](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/autofit_profiling_bootstrap.md) — active: B4a (autofit_profiling#3) and B4b (autofit_profiling#5, issue #4 closed, merged 2026-10-15) shipped: search.fit breakdown cell, profiling-summary@2 exporter, EP/graphical N3/N10/N30 baselines and analytic parity cell; #6 repointed RAL paths to the category layout (2026-10-15). Pulse fit fixture/campaign merged (#60, #61); fit receipt ok at autofit_profiling 58e56b9 (31 records, fetched 2026-10-15T22:58Z), so the post-deploy refresh is done. Epic 2 not opened: next bounded step is a human-scoped epic-2 campaign row; B5c inference work belongs to Insight, not Pulse.

</details>

<details><summary>Critical curves and evaluation grids — needs-decision</summary>

Reviewed 2026-10-17. No new campaign measurement. Phase 3b cap fix remains shipped; project wiki still incorrectly says #646 awaits merge/release. Seed coverage and path completion remain unresolved; retain marching-squares decision and ask the human whether to scope the next phase. Check-in 2026-10-17: no project wiki/results/issue change since 2026-10-13 beyond autolens_profiling#420/#422/#424 (interferometer only); releases 2026.10.16.1/.2 and 2026.10.17.1 supply no new measurement.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/critical_curves.md)

### Active tasks


</details>

<details><summary>Certified positive solver — parked</summary>

Reviewed 2026-10-17. Parked unchanged. No new campaign evidence; existing C2/library/workspace drafts remain pending. Do not infer admission from solver timing, and do not change default or restart the campaign. Check-in 2026-10-17: no project wiki/results/issue change since 2026-10-13 beyond autolens_profiling#420/#422/#424 (interferometer only); releases 2026.10.16.1/.2 and 2026.10.17.1 supply no new measurement.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/certified_positive_solver.md)

### Active tasks


</details>

## Profiling Results

Choose a project, dataset and model on the interactive board.

[Interactive board](https://pyautolabs.github.io/PyAutoPulse/)

<details><summary>autolens — optimal, current setups</summary>

[Interactive setup browser](https://pyautolabs.github.io/autolens_profiling/)

126 current · 319 superseded · 99 archived (counted, not shown). Class and status are the producer's declarations.

| Likelihood | Instrument | Setup | Hardware class | Model variant | Measurement | Value (producer) | Decision |
|---|---|---|---|---|---|---:|---|

Coverage: 90 optimal cell(s) not measured.

- cluster/image_plane · simple · jax_gpu_na_fp64 · hpc_a100 · default · runtime
- cluster/image_plane · simple · jax_gpu_na_fp64 · hpc_a100 · default · breakdown
- cluster/image_plane · simple · jax_cpu_na_fp64 · hpc_ral_cpu · default · runtime
- cluster/image_plane · simple · jax_cpu_na_fp64 · hpc_ral_cpu · default · breakdown
- datacube/delaunay · alma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- datacube/delaunay · alma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · breakdown
- datacube/delaunay · alma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- datacube/delaunay · alma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · breakdown
- datacube/delaunay · alma_high · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- datacube/delaunay · alma_high · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · breakdown
- datacube/delaunay · alma_high · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- datacube/delaunay · alma_high · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · breakdown
- datacube/delaunay · sma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- datacube/delaunay · sma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · breakdown
- datacube/delaunay · sma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- datacube/delaunay · sma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · breakdown
- imaging/delaunay · ao · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/delaunay · ao · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/delaunay · ao · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/delaunay · ao · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/delaunay · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/delaunay · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/delaunay · euclid · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/delaunay · euclid · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/delaunay · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/delaunay · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/delaunay · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/delaunay · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/delaunay · jwst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/delaunay · jwst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/delaunay_nn · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/delaunay_nn · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/mge · ao · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/mge · ao · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/mge · ao · jax_cpu_dense_fp64 · hpc_ral_cpu · default · runtime
- imaging/mge · ao · jax_cpu_dense_fp64 · hpc_ral_cpu · default · breakdown
- imaging/mge · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/mge · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/mge · euclid · jax_cpu_dense_fp64 · hpc_ral_cpu · default · runtime
- imaging/mge · euclid · jax_cpu_dense_fp64 · hpc_ral_cpu · default · breakdown
- imaging/mge · hst · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/mge · hst · jax_cpu_dense_fp64 · hpc_ral_cpu · default · runtime
- imaging/mge · hst · jax_cpu_dense_fp64 · hpc_ral_cpu · default · breakdown
- imaging/mge · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/mge · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/mge · jwst · jax_cpu_dense_fp64 · hpc_ral_cpu · default · runtime
- imaging/mge · jwst · jax_cpu_dense_fp64 · hpc_ral_cpu · default · breakdown
- imaging/rectangular · ao · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/rectangular · ao · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/rectangular · ao · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/rectangular · ao · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/rectangular · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/rectangular · euclid · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/rectangular · euclid · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/rectangular · euclid · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/rectangular · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/rectangular · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- imaging/rectangular · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- imaging/rectangular · jwst · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- imaging/rectangular · jwst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- imaging/rectangular · jwst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- interferometer/delaunay · alma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/delaunay · alma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/delaunay · alma_high · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/delaunay · alma_high · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/delaunay · jvla · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/delaunay · jvla · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/delaunay · jvla · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · breakdown
- interferometer/delaunay · sma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/delaunay · sma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/mge · sma · jax_gpu_dense_fp64_nufft · hpc_a100 · default · runtime
- interferometer/mge · sma · jax_cpu_dense_fp64_nufft · hpc_ral_cpu · default · runtime
- interferometer/mge · sma · jax_cpu_dense_fp64_nufft · hpc_ral_cpu · default · breakdown
- interferometer/rectangular · alma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/rectangular · alma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/rectangular · alma_high · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/rectangular · alma_high · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/rectangular · jvla · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/rectangular · jvla · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- interferometer/rectangular · jvla · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · breakdown
- interferometer/rectangular · sma · jax_gpu_sparse_fp64_wtilde · hpc_a100 · default · runtime
- interferometer/rectangular · sma · numba_cpu_sparse_fp64_wtilde · hpc_ral_cpu · default · runtime
- multi_dataset/delaunay · hst · jax_gpu_dense_fp64 · hpc_a100 · default · runtime
- multi_dataset/delaunay · hst · jax_gpu_dense_fp64 · hpc_a100 · default · breakdown
- multi_dataset/delaunay · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · runtime
- multi_dataset/delaunay · hst · numba_cpu_sparse_fp64 · hpc_ral_cpu · default · breakdown
- point_source_image/image_plane · simple · jax_gpu_na_fp64 · hpc_a100 · default · runtime
- point_source_image/image_plane · simple · jax_cpu_na_fp64 · hpc_ral_cpu · default · runtime
- point_source_source/source_plane · simple · jax_cpu_na_fp64 · hpc_a100 · default · runtime
- point_source_source/source_plane · simple · jax_cpu_na_fp64 · hpc_a100 · default · breakdown

</details>

<details><summary>Capture, qualification and legacy diagnostics</summary>


## lens

<!-- pulse:instance name=lens receipt=e1f52f4794265119e126de728be2e5990b0e63cd outcome=ok shown=e1f52f4794265119e126de728be2e5990b0e63cd -->

Project `autolens_profiling`, scope `likelihood-lifecycle`, read from [PyAutoLabs/autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling) `dashboard/catalogue.json` at [`e1f52f47`](https://github.com/PyAutoLabs/autolens_profiling/tree/e1f52f4794265119e126de728be2e5990b0e63cd); producer revision `1f3d336d`; generated 2026-10-24T13:12:04Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autolens_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/lens.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · evidence time unknown (evidence unknown (No common measurement wall-clock across legacy evidence; inspect each record's measured_at.))
- **Qualification:** 0/445 records · 0/0 comparisons qualified
- **Lifecycle:** 126 current · 319 superseded · 99 archived (producer-declared)

### lens / limitations

- Phase-0 labels (autolens_profiling#442): nothing was re-measured. A current record is the canonical cell row on a reference host class for a planned baseline cell; it is not an accepted baseline and carries no day_zero stamp.
- No designation decision exists yet: provisional Optimal rows are class secondary with 'provisional_optimal: true' in their limitations (R3); planned_cells carry the provisional class.
- Standard source-pixel counts are Delaunay 1250 and rectangular 1225 (35x35). No committed row is at the standard size; current pixelized rows carry a size_fallback limitation.
- Records whose key has no current row (laptop-only, experiment-only, or outside the planned cells) are not rendered; coverage.excluded counts them per key. Every row stays in the companion v2 setup catalogue (dashboard/catalogue/setups.json).
- Historical recommendations and hazard findings name v2 setups and stay in the companion catalogue until they are re-bound to v3 setup_ids.
- Parity records (measurement parity) transcribe a cell's parity.json witness: metric abs_delta_log_likelihood = \|log L - reference log L\| beside its tolerance, the signed values and the witness status in the record's parity block. A not_assessed witness has no value and yields no record; parity_witnesses lists every witness file.

### lens / excluded by the producer

- `no-current/fa262c42d1c1fa9abab8`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/b74ff954389bac73c0a8`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/a34872fd7c903ef8d000`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/36547b1b316c2dab4c2e`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/478b9b5c5f35f7b0fb61`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/6a76add1c536baf31685`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/5376e5d1b8f00b4f6e78`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/5c24ba04fa0343afbbec`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/7cb5611f3c6175283d2e`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/3de4a78aab8eac55ba0c`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/aa4597cf89f849903cf6`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/670498455c76cf8f0df5`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/fa4ba3f437dae2a5b2a5`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/39a4c0dd138cbe5b5e98`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/65407474fe2e4ef8b628`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/c60302d2a01d3deae2c7`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/3e6c652ca2b5e13e724c`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/a5055066b8551ef44ef6`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/9aa64cf8a3e905866534`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/4827c875cd4829835031`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/ce1a16ae9f3a8641deff`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/d78d2cce21403da69323`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/c942faee01a635763191`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_dense_mixed_nufft/hpc_a100/breakdown.json))
- `no-current/43e54c157c12c0d8bf9a`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/jvla/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/4a0a7126ca43990f501e`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/a4ea3fd3c1790e259fb3`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/2f4258e5f9ae9da1d510`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/40faeb7b8e8abca042bc`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/c5c6c00e28116c0255e7`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/4ef0be66369e1a15ce8b`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/e8b56a1e92c9133ebcd0`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/de3e1a4c6f03fcab2e97`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_dense_fp64_nufft/hpc_a100/breakdown.json))
- `no-current/3a0362eb1742ac250c1d`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/37f546d43937aba98b62`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/e2c8effc98834ffad93d`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/caf9037151cb3dcba4c3`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/jax_gpu_sparse_fp64_wtilde/hpc_a100/breakdown.json))
- `no-current/30074e4c94cb3b07f776`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/7f37c2de31224c053e38`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/7f880a624b1fc3d8ad2e`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/delaunay/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/7cabce54a4d710b37313`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/0522961f290c51012998`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/7cff33aa7f2488078c8c`: No current record on this key: likelihood x instrument is not a planned baseline cell. Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/rectangular/sdp81/numba_cpu_sparse_fp64_wtilde/hpc_ral_cpu/breakdown.json))
- `no-current/abcb15986b8ebabbefbb`: No current record on this key: scan/experiment/history rows only (never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/cluster/image_plane/simple/jax_cpu_na_fp64/hpc_ral_cpu/experiments/robust_settings_sweep/breakdown.json))
- `no-current/b351c674fdc3e083bf5a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_gpu_dense_fp64/local_gpu/light_fixed/experiments/library_n1250/breakdown.json))
- `no-current/e3d35b23d1be0342b7d8`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library_n1250/breakdown.json))
- `no-current/64ae10651fe338e809e7`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_gpu_dense_fp64/local_gpu/light_fixed/experiments/library_n1250/breakdown.json))
- `no-current/e5dce29a60b6062d02a2`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library_n1250/breakdown.json))
- `no-current/43ed3d6b081673ee6f1e`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/euclid/jax_gpu_dense_fp64/local_gpu/light_fixed/experiments/library_n1225/breakdown.json))
- `no-current/e9aacc78f8268011feff`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/euclid/jax_gpu_dense_fp64/local_gpu/light_fixed/experiments/library_n1225/breakdown.json))
- `no-current/f1b963e99a30d4ee7a7f`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/054577b909c4a27c55da`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/f4a1f86043bfaf914092`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay_nn/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/52fa22cdedf5dfe3d27e`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay_nn/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/747901abe91e8cf66ba8`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/d58f51a179f973738a84`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_gpu_dense_mixed/local_gpu/light_fixed/experiments/library/breakdown.json))
- `no-current/2823c0a983875776d0c0`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/5f07d914f57a89946273`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/16692cb897cd5313ba95`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/311338dc332372387f08`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/906dfe7b1c15e4742268`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/02d2602e1b2022f6a6ee`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/d9a1484262b944bbd9b4`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/7373af4cacf924e8bc7a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/d9b55b76942e62a2996b`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/alma_high/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/f0dc02b1ba248f536d6a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/ao/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/6082b6baacd171b4426e`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/ao/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/25bcd73dc6490a64f366`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_n1250_t8/breakdown.json))
- `no-current/efc004dfc5ee3c5418c6`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/euclid/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_n1250_t8/breakdown.json))
- `no-current/abae43b4c2f50a24076a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_n1250_t8/breakdown.json))
- `no-current/781d0695c9cd126bf3d2`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_n1250_t8/breakdown.json))
- `no-current/9cd77dc68e0000751852`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/caa47b87284e5968862d`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/2f732043751cecbcb55d`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/49470034cab63b4b64c0`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/hst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/130c816e748e9500ff11`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay_nn/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_t1/breakdown.json))
- `no-current/79df5eb9720a1775ebbe`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay_nn/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_t1/breakdown.json))
- `no-current/a4df8bd631a3520fd198`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/hst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/f6980fd6171c49ab85c7`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/hst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/d6184dffa97755cec6de`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/hst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/c4d3bb181b106195d8c6`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/hst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/b1e6e94aae18196e10b5`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_t1/breakdown.json))
- `no-current/93db90031f651a2865fe`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_dense_fp64/local_laptop/light_fixed/experiments/library_t1/breakdown.json))
- `no-current/13c6c796790c86544384`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/e0d6cd05441853b74ee3`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/d5158054f3fa97a736c5`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/7a155fa11f8a3bf438e4`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/65d04b6539e893e55d2a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/hst/numba_cpu_sparse_fp64/local_laptop/mge_mass/runtime.json))
- `no-current/d676a7001e8404f308fc`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/jwst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/fbabe5af862d5d57ecea`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/jwst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/ca897f6598709a1cdbab`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/jwst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/5b0b37f1b0c54124b299`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/delaunay/jwst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/6d5cf0a365fe8c1fd996`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/jwst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/a1a8c9eec7c377ffd263`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/jwst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/a2a4d4d44f876d1c5764`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/jwst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/4099e543a398efa65e92`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/mge/jwst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/fd1c32a4d7217577a927`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/jwst/jax_cpu_dense_fp64/local_laptop/runtime.json))
- `no-current/fbd87b11ddc0a91f381c`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/jwst/jax_cpu_dense_mixed/local_laptop/runtime.json))
- `no-current/4fc25982979e8f7da393`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/jwst/jax_cpu_sparse_fp64/local_laptop/runtime.json))
- `no-current/8a2e3526022376745424`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/imaging/rectangular/jwst/jax_cpu_sparse_mixed/local_laptop/runtime.json))
- `no-current/ed3ff7c29ae68ce4ad38`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/cluster/image_plane/simple/jax_cpu_na_fp64/local_laptop/experiments/robust_settings_sweep_draws53_73_81/breakdown.json))
- `no-current/b1c65d5790cf8f9294cd`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/a4c00d29b360c75d4519`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/edba7fb2d4a1bc157a35`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/0ffc1db48feb05c81f95`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/0499ee37058c2a0db0ce`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_dense_fp64_nufft/local_laptop/breakdown.json))
- `no-current/764f45baac5e3ebbfa7a`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_sparse_fp64_wtilde/local_laptop/breakdown.json))
- `no-current/9ec45abe77a5ecec9a83`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_dense_fp64_nufft/local_laptop/runtime.json))
- `no-current/2f7c6acd428a359eecaa`: No current record on this key: laptop/local-GPU rows only (R7: never current). Kept in the companion v2 catalogue. ([evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/e1f52f4794265119e126de728be2e5990b0e63cd/results/interferometer/mge/sma/jax_cpu_dense_mixed_nufft/local_laptop/runtime.json))
</details>

<details><summary>autofit — choose a setup</summary>

[Interactive setup browser](https://pyautolabs.github.io/autofit_profiling/)

<details><summary>analytic_gaussian</summary>

- **conjugate hierarchical gaussian**: unspecified

</details>

<details><summary>gaussian_1d_ep</summary>

- **gaussian, centre shared across datasets**: unspecified

</details>

<details><summary>gaussian_x1</summary>

- **gaussian**: unspecified

</details>

</details>

<details><summary>Capture, qualification and legacy diagnostics</summary>


## fit

<!-- pulse:instance name=fit receipt=0481145eee4a01c62b4cbfd87a57de01ce40655a outcome=ok shown=0481145eee4a01c62b4cbfd87a57de01ce40655a -->

Project `autofit_profiling`, scope `pyautofit-profiling`, read from [PyAutoLabs/autofit_profiling](https://github.com/PyAutoLabs/autofit_profiling) `dashboard/catalogue.json` at [`0481145e`](https://github.com/PyAutoLabs/autofit_profiling/tree/0481145eee4a01c62b4cbfd87a57de01ce40655a); producer revision `—`; generated 2026-10-14T14:45:45Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autofit_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/fit.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · age 9 d at fetch 2026-10-23 (evidence 2026-10-14)
- **Qualification:** 31/31 records · 0/0 comparisons qualified

### fit / limitations

- Laptop CPU only, pinned to one host (DESKTOP-H143S82, WSL2) so Pulse's same-host rule pairs every record; the epic's release-sweep pin (euclid-ral-gpu-2, an A100 node) does not fit CPU Dynesty runs. Cross-machine reproduction on RAL is a later campaign.
- Wall times vary up to ±40 % between sessions on this host, so breakdown shares are the comparable quantity, not seconds; the EP / graphical / parity rows are single fresh-process fits (repetitions 1).
- Component times are exclusive monkey-patched wall-clock intervals; 'other' is wall minus the instrumented total, not a measured phase.
- The EP / graphical rows carry a producer-side reproduction note against the committed autofit_workspace_developer baselines (runtime-drift-2x-1ms, in each row's `reference`); it is not a Pulse comparison, because those baselines recorded no host and no record pair exists.
- The N30 EP and graphical rows reproduce the committed sanity FAIL; their wall and memory are real measurements of a fit whose parameter recovery fails, not of a correct fit.
- Every record is unreviewed: the producer declares measurements, the Brain's profiling conductor judges them; nothing here is a verdict.
- No temporal comparisons: one baseline per setup.
</details>

<details><summary>autolens_inference — wall-time validation</summary>

Full-fit measurements: one sampler run per row. Every derived number is the producer's; Pulse computes no ratio and never reads a full-fit time as a per-likelihood measurement.

| Likelihood | Instrument | Setup | Hardware class | Model variant | Sampler | Seed | Cores | Wall s | Likelihood evals | Implied ms/eval | Predicted ms/eval | Measured/predicted | Parallel efficiency | Parity | Reference runtime record | Release |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| imaging/delaunay | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:mass_total[1] | 1 | 8 | 8648.197281122208 | 38660 | 223.69884327786363 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/delaunay | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[2] | 1 | 8 | 453.9056279659271 | 2120 | 214.1064282858147 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/delaunay | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[1] | 1 | 8 | 12609.190230846405 | 53920 | 233.84996718928795 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/delaunay | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:light[1] | 1 | 8 | 2269.41446018219 | 10180 | 222.928728898054 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/delaunay | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | light_fixed | nautilus:mass_total[1] | 1 | 8 | 4563.577402114868 | 34060 | 133.98641814782349 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 0 | 8 | 32440.87102484703 | 30400 | 1067.1339152910207 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 0 | 8 | 5783.566254377365 | 5560 | 1040.2097579815406 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 0 | 8 | 38212.712732076645 | 34540 | 1106.3321578481946 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:light[1] | 0 | 8 | 5446.4585750103 | 11080 | 491.5576331236732 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 0 | 8 | 3367.1460740566254 | 92550 | 36.38191327992032 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 1 | 8 | 24129.204991340637 | 22020 | 1095.7858760826812 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 1 | 8 | 4042.287693500519 | 3720 | 1086.6364767474513 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 1 | 8 | 38641.76520562172 | 34180 | 1130.5373085319404 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:light[1] | 1 | 8 | 5703.012356042862 | 10620 | 537.0068131867101 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 1 | 8 | 3410.500566005707 | 91250 | 37.375348668555695 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_sparse_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 0 | 8 | 36050.4700050354 | 21720 | 1659.78222859279 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 0 | 8 | 6332.766473293304 | 3820 | 1657.7922704956293 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 0 | 8 | 83132.6692700386 | 34540 | 2406.852034453926 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_sparse_fp64 | hpc_a100 | default | nautilus:light[1] | 0 | 8 | 3972.188988685608 | 10880 | 365.0908996953684 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_sparse_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 0 | 8 | 3471.9577021598816 | 92550 | 37.51439980723805 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 0 | 4 | 558.6179111003876 | 23680 | 23.590283407955553 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 0 | 4 | 181.06282258033752 | 7800 | 23.21318238209455 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 0 | 4 | 700.8667027950287 | 33020 | 21.225520981072947 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:light[1] | 0 | 4 | 234.4628677368164 | 11600 | 20.21231618420831 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 0 | 4 | 714.9393587112427 | 92550 | 7.724898527404027 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 1 | 4 | 524.995144367218 | 21640 | 24.26040408351285 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 1 | 4 | 130.3421642780304 | 5000 | 26.06843285560608 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 1 | 4 | 732.5671072006226 | 34520 | 21.22152685980946 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:light[1] | 1 | 4 | 219.77784371376038 | 10100 | 21.76018254591687 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 1 | 4 | 712.3624505996704 | 87700 | 8.122718935001943 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 0 | 4 | 826.8618957996368 | 23060 | 35.85697726798078 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 0 | 4 | 298.14068365097046 | 8140 | 36.62661961314134 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 0 | 4 | 1786.1555726528168 | 32820 | 54.42277796017114 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:light[1] | 0 | 4 | 221.9318356513977 | 11100 | 19.993859067693485 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 0 | 4 | 714.965235710144 | 92550 | 7.725178127608256 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:mass_total[1] | 1 | 4 | 811.5136122703552 | 22980 | 35.31390827982399 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[2] | 1 | 4 | 226.34285354614258 | 6000 | 37.723808924357094 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_pix[1] | 1 | 4 | 1648.602859735489 | 30360 | 54.30180697415971 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:light[1] | 1 | 4 | 196.74390411376953 | 9200 | 21.385206968887992 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | default | nautilus:source_lp[1] | 1 | 4 | 719.88591837883 | 87700 | 8.208505340693614 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:mass_total[1] | 0 | 8 | 2605.161903142929 | 22920 | 113.66325929942973 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[2] | 0 | 8 | 579.7866718769073 | 5660 | 102.43580775210377 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[1] | 0 | 8 | 4961.520958900452 | 33660 | 147.40109800654935 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:light[1] | 0 | 8 | 1275.32878780365 | 10520 | 121.22897222468156 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:mass_total[1] | 1 | 8 | 2562.1093657016754 | 22240 | 115.20275924917605 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[2] | 1 | 8 | 939.1733293533325 | 9460 | 99.278364625088 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:source_pix[1] | 1 | 8 | 4867.771735191345 | 33200 | 146.61963057805258 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | default | nautilus:light[1] | 1 | 8 | 1478.9101498126984 | 12000 | 123.24251248439153 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 0 | 8 | 21738.99609732628 | 23780 | 914.1714086344103 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_cpu_dense_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 1 | 8 | 20092.072603940964 | 20940 | 959.506810121345 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 0 | 4 | 490.45253920555115 | 22820 | 21.492223453354562 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_dense_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 1 | 4 | 449.70745611190796 | 20780 | 21.64135977439403 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 0 | 4 | 1624.8536005020142 | 48700 | 33.36455031831651 | — | — | — | diverged | — | 2026.10.17.1 |
| imaging/rectangular | hst | jax_gpu_sparse_fp64 | hpc_a100 | light_fixed | nautilus:mass_total[1] | 1 | 4 | 1396.915834903717 | 41880 | 33.35520140648799 | — | — | — | diverged | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | light_fixed | nautilus:mass_total[1] | 0 | 8 | 2329.3615324497223 | 24340 | 95.70096682209213 | — | — | — | not_assessed | — | 2026.10.17.1 |
| imaging/rectangular | hst | numba_cpu_sparse_fp64 | hpc_ral_cpu | light_fixed | nautilus:mass_total[1] | 1 | 8 | 2076.24631023407 | 21960 | 94.54673543870992 | — | — | — | not_assessed | — | 2026.10.17.1 |

</details>

<details><summary>Capture, qualification and legacy diagnostics</summary>


## lens-walltime

<!-- pulse:instance name=lens-walltime receipt=db905284f6fad18e33962165793278ee3333e256 outcome=ok shown=db905284f6fad18e33962165793278ee3333e256 -->

Project `autolens_inference`, scope `None`, read from [PyAutoLabs/autolens_inference](https://github.com/PyAutoLabs/autolens_inference) `dashboard/walltime_validation.json` at [`db905284`](https://github.com/PyAutoLabs/autolens_inference/tree/db905284f6fad18e33962165793278ee3333e256); producer revision `c356209a`; generated 2026-10-23T14:10:37Z; comparison policy `None`. [Project dashboard](https://pyautolabs.github.io/autolens_inference/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/lens-walltime.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · evidence time unknown (evidence unknown (no reason given))
- **Qualification:** 56 full-fit records (walltime-validation carries no qualification flag)

### lens-walltime / limitations

- Full-fit measurements: one Nautilus stage of one SLaM chain per record, never a per-likelihood cost; the sampler is <sampler>:<stage> because the key has no stage
- wall_s is the sampler clock (samples_info.json) and includes sampler overhead; implied_ms_per_eval = wall_s / likelihood_evals * 1000 is therefore an upper bound on the per-evaluation cost
- parallel_efficiency is null: no 1-core row of any key exists yet
- parity_status is not_assessed unless a declared ruling of record names the run (parity_basis); the exporter computes no parity verdict
- 56 of 56 records have no Pulse runtime reference: the lens snapshot's runtime records do not determine the operator (dense/sparse) or match the instrument and mesh, so reference_runtime_record_id and predicted_ms_per_eval are null until the lens pin moves to profiling-summary@3
- 17 CPU-backend record(s) keep host_class hpc_a100 from their config prefix: the row records no host that proves a RAL CPU node
- 6 stage(s) omitted: stages loaded from another config (--stages-from) are not this run's fit
- 33 stage(s) omitted: non-default model-variant stages identical to the default run's (one --lens-light both job, one fit) are listed once, under default
</details>


<!-- decision-history:4d88bb773a36f774562f9e06d52a024b839cc44d2aa91282311891f6064c43c3 -->
## Decision History

- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/cluster-pointsolver-starting-grid.md">Keep the 1.0″ PointSolver starting grid for cluster fits, with a validation check</a>
- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/direct-conv-symmetric-gate.md">Gate the symmetric direct_conv kernel at work fraction 0.7, with ymin column ordering</a>
- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/interferometer-route-gate-cost-model.md">Route interferometer curvature by a calibrated two-constant cost model</a>
- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/adaptsplit-zero-weight-delaunay-only.md">Exclude zero-weight mappings from AdaptSplit pixel signals on Delaunay meshes only</a>
- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md">Keep Jacobi PDIP as the Mapper default and raw+polish as the MGE-only default</a>
