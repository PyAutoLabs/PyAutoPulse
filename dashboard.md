# PyAutoPulse — profiling dashboard

<!-- pulse-campaigns:cbea1eba629dc0064077ad5d1af613005d3a58f8a6d17b54b253eb6468e6d379 -->
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

Last check-in: 2026-10-04T17:18:38Z (review date, not measurement freshness).

## Active campaigns

<details><summary>Setup baseline collection and scientific acceptance — needs-decision</summary>

Reviewed 2026-10-06. Specification is draft (autolens_profiling#384); no baseline collection or acceptance authorized. Resolve immutable software and dependency lock, dataset hashes/settings, hardware/threads/load and timing/cache/memory methodology/witnesses; freeze the manifest before separately authorizing collection. Compile probe builder remains unavailable; archived timings are context only.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/62a6ad1e82735e360c7cf25be62253a286493b17/wiki/campaigns/setup_baseline.md)

### Active tasks

- [Freeze the setup baseline specification, then collect and review evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/setup_baseline_campaign.md) — needs-decision: Human resolves draft manifest choices and freezes the specification; collection requires separate compute authorization. The report prepares evidence for human scientific review and never promotes baselines. CPU production arrays use ral only; compile capability gap remains open.

</details>

<details><summary>Point-source image plane · CPU — active</summary>

Reviewed 2026-10-04. Phases 1–4 shipped; PyAutoLens#764 (extent warning) released in 2026.10.4.1. Next: docs-only autolens_profiling PR writing campaign completion evidence and fixing stale wiki/index lines (#763 &#x27;in flight&#x27; → #764 merged). RAL leftover folders present; mirror sync unverified.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/point_source_image_plane_cpu.md)

### Active tasks

- [Point-source (single-source) CPU campaign — carried leftovers and completion evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pointsolver_cpu_speed_campaign_remainder.md) — ready: Execution 2026-10-04: docs-only branch feature/point-source-wiki-reconcile @0560284 (issue autolens_profiling#370), parked at Heart RED. Still owed: RAL cleanup, register_model grad-zero prompt, test move, CI smoke cells, nopad deletion.

</details>

<details><summary>Point-source image plane · A100 — needs-decision</summary>

Reviewed 2026-10-04. Phase 0+1 shipped (profiling#353 merged 2026-09-30; wiki stale). Forward-mode gradient NaN is unfixed and live in 2026.10.4.1 but only a Mind draft. Human decisions: issue that bug; authorize the autolens_inference image-plane fit measurement.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/point_source_gpu_breakdown.md)

### Active tasks

- [Point-source A100 speed-up campaign: profile and optimize with the shared breakdown](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_image_plane_gpu_breakdown.md) — needs-decision: Execution 2026-10-04: forward-mode NaN issued as PyAutoLens#767 (reproduced on CPU fp64: forward [nan]x5, reverse finite; stack 2026.10.4.1+3 b695e57b6); Mind registry 0112ccba. The autolens_inference image-plane fit measurement still awaits human authorisation.

</details>

<details><summary>Point-source source plane — parked</summary>

Reviewed 2026-10-04. Core complete. Nautilus leaf autolens_inference#17 merged 2026-10-02 (wiki still says open). Blackjax parked: gradient-sampler admission not met. Warm-up task awaits the human&#x27;s option (a)/(b)/(c).

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/point_source_source_plane.md)

### Active tasks

- [Runtime cells&#x27; A100 `single_jit` includes the post-compile warm-up — source-plane 0.642 ms vs a steady 0.267 ms on the same node](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/runtime_cell_single_jit_gpu_warmup.md) — active: Execution 2026-10-04: human chose option (a). Branch feature/runtime-single-jit-median @87a7fcc (issue autolens_profiling#371) parked at Heart RED. Local CPU witness: single_jit 0.417 ms, median 0.388 ms (p10 0.320, p90 0.545). Imaging cells not yet wired.
- [Point-source source-plane chi-squared speed-up campaign — remaining candidates (phases 1–2e shipped)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_source_plane_chi_squared_speed.md) — blocked: Still blocked: gradient-sampler admission not met (autolens_inference has only the Nautilus source-plane leaf, #17 merged 2026-10-02). Blackjax stays parked.

</details>

<details><summary>Cluster PointSolver robustness and performance — active</summary>

Reviewed 2026-10-04. Unchanged since 2026-09-27; nothing issued or claimed. Wiki still points at the removed Mind draft (now Pulse tasks/). Pick one bounded phase: observable-overflow invalid-result policy + CI witness, or a representative-data baseline cell.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/cluster_pointsolver.md)

### Active tasks

- [Cluster PointSolver — robustness, analysis settings and performance](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/cluster_pointsolver_speed.md) — ready: Unissued, no claim. Pick one bounded phase per Mind epics.md: observable-overflow invalid-result policy + CI witness, or a representative-data baseline cell.
- [PointSolver profiling cells: lensed quasar → cluster runtime tier → single/multi-source → multiplane](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_solver_profiling_cells.md) — ready: Unissued, no claim. Candidate first cell: a representative-data cluster likelihood_runtime baseline (single-source preset).

</details>

<details><summary>Interferometer likelihood and streaming — active</summary>

Reviewed 2026-10-04. Last CPU cell ran (RAL job 375978_3 COMPLETED 1:11:36, JSON on RAL, not on main) but misses the ≤1e-3 nat CPU/A100 witness: human decision needed. Streaming phases 3–5 shipped; the scaling measurement needs compute authorization. Curvature, memo and FFT tasks unstarted.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/interferometer_likelihood.md)

### Active tasks

- [Interferometer decision matrix — fill the last cell (CPU rect 39² at alma_high r5.0) and flip the wiki row to shipped](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_decision_matrix_last_cell.md) — active: Execution 2026-10-04: human decision ACCEPT the 1.59e-3 nat CPU/A100 gap (precedent r3.5 at 1.5e-3). Branch feature/interferometer-decision-matrix-last-cell @93a002a committed locally; ship PARKED at Heart RED (release validation FAILED, stage integrate). Caveat: the A100 row&#x27;s own A/B shows certified solver = PDIP to 0.0 nat, so the gap may be F/D on older revisions rather than solver. Correction: PyAutoArray#582 first released 2026.9.27.2. Next: ship once Heart clears.
- [Interferometer fixed-mapper searches: reuse the W~ curvature matrix across likelihood calls via `preloads.curvature_matrix`](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_fixed_mapper_curvature_preload.md) — ready: Phase 1 sliced 2026-10-04 into a Mind draft (PyAutoArray preload plumbing + CPU breakdown lever, no GPU); run it through start_dev. Human science call first - no production SLaM stage holds the mapper fixed today.
- [fnnls warm-start memo: stop it slowing scattered evaluation streams (interferometer CPU, autolens_profiling#332)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_nnls_memo_scattered_stream_guard.md) — ready: Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.
- [Campaign: interferometer streaming (array-free) vs in-memory — memory and time scaling to 2e8 visibilities](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_streaming_scaling.md) — active: Execution 2026-10-04: branch feature/interferometer-streaming-scaling @4a0ef46 (issue autolens_profiling#368) parked at Heart RED. Laptop CPU 8-thread indicative rows recorded (chunk 65536 to 5e7 vis; in-memory first failure 1e6 under a 10 GB cap; parity 1.2e-9 nats at 5e5; 1e8 skipped). Go/no-go overtaken; recorded as release evidence for 2026.10.4.1. nufft_chunk_size arm hits a second memory wall in transformer.image_from (library candidate, no issue filed).
- [Interferometer W~ curvature matrix is FFT-bound on the mask extent: pruned padded FFT and real-space pixel scale on the A100](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_w_tilde_fft_size_levers.md) — ready: Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.

</details>

<details><summary>Linear-solver accuracy and cost — blocked</summary>

Reviewed 2026-10-04. Release half met: PyAutoArray#595 is in 2026.10.2.1 and 2026.10.4.1. RAL mirror sync (HPCPullPyAuto, plus a dependency-floor diff) unverified; phase 3 GPU/vmap parity and timing waits on it.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/linear_solver_accuracy.md)

### Active tasks

- [Linear-solver programme phase 3: GPU/vmap/A100 timing and parity rows for the solver corpus](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/mge_nnls_fix_pyautoarray_571_slam_60.md) — blocked: RAL sync SKIPPED 2026-10-04: 180 euclid_dr1 tasks RUNNING on the shared base; mirror at 2026-09-27 state, 16–35 commits behind tag 2026.10.4.1; a sync pulls MAINS and also needs a jax reinstall (Nerves main excludes jax 0.10.2). Next: sync when `squeue -u jnightin -t R` shows no euclid_dr1 jobs on the shared base, or the human accepts the risk.

</details>

<details><summary>Production imaging and likelihood breakdown — active</summary>

Reviewed 2026-10-04. No new results since the pin. Over-sampling phase 1: add --instrument production presets to the JAX Delaunay cells (CPU smoke only); PyAutoArray#606 S/N over-sampling helper (in 2026.10.4.1) is new context. Post-certified Blocked-by is stale (resolved 2026-09-27).

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/post_certified_breakdown.md)

### Active tasks

- [Profile imaging pixelizations at production over-sampling](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/imaging_production_over_sampling.md) — ready: Phase 1 (workspace-only): --instrument euclid\|hst presets for the JAX Delaunay runtime/breakdown cells, keeping flat-1 selectable; CPU smoke only. A100 re-measure is a separate compute-authorized phase.
- [Assess remaining likelihood bottlenecks after certified solver integration on CPU and GPUs](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/post_certified_solver_likelihood_breakdown.md) — needs-slicing: Blocked-by is stale: resolved 2026-09-27 (PyAutoArray#567 in 2026.9.26.1). Unissued; scope one bounded phase from the full task contract.
- [Quick-update plotting cost — minutes per update, and it is not JAX compile](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/quick_update_plotting_cost.md) — ready: Unchanged; targets PyAutoLens/PyAutoGalaxy (PyAutoLens#680 closed 2026-07-31, no follow-up issue). Select one bounded step when prioritised.

</details>

<details><summary>Measurement reliability and profiling tools — active</summary>

Reviewed 2026-10-04. Only timing_noise_audit is issued (autolens_profiling#362: open, no comments, unassigned); start its audit phase via start_dev. Other nine tasks unchanged and unissued; mass_field superseded confirmed.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoPulse/tree/f1801514ddcf2272b832c2b53713cd2257aea5c0/tasks)

### Active tasks

- [Audit timing tests and profiling gates for measurement noise](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/timing_noise_audit.md) — ready: Issued as autolens_profiling#362 (open, 0 comments, unassigned). Start its read-and-classify audit phase via start_dev.
- [MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/mge_likelihood_breakdown_steps_are_cumulative_an.md) — ready: Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.
- [A gradient-cost probe: forward vs `value_and_grad` ms/eval and a strict FD check, on any registry cell](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_cost_probe.md) — ready: Unchanged and unissued (workspace_developer#117 closed 2026-07-28). Select one bounded step when prioritised.
- [Numba breakdown harness: perturb the instance so the operated-matrix memo cannot hide a step](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/numba_breakdown_harness_memo_blind.md) — ready: Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.
- [Search settings-estimation + profiling infrastructure (n_starts / batch_size / n_batch)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/search_settings_estimation_infrastructure.md) — ready: Unchanged and unissued (autolens_profiling#82 closed 2026-08-18). Select one bounded step when prioritised.
- [jax_compile/probe.py lost its cell builder with the searches tier — give profiling its own](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/jax_compile_probe_needs_own_cell_builder.md) — ready: Unchanged and unissued; scripts/misc/jax_compile/probe.py still on main (run state unverified). Select one bounded step when prioritised.
- [profile_lens_aggregator.py cannot run from the autolens_workspace_developer root: no config/ directory](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/profile_lens_aggregator_needs_config_dir.md) — ready: Unchanged: workspace_developer main still has no root config/ (bug presumed live, not re-run). Select one bounded step when prioritised.
- [jax_profiling/gradient/imaging/pixelization.py: 3.2% of its pin move is unattributed](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_pixelization_pin_residual_drift.md) — ready: Unchanged and unissued (PyAutoArray#490 merged 2026-08-26). Select one bounded step when prioritised.
- [Pair JAX/XLA env vars with measured compile and run times, per backend](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pair_jax_xla_env_vars_with_measured.md) — ready: Unchanged and unissued. Context: jax-version policy changes merged to library mains 2026-10-04, unreleased. Select one bounded step when prioritised.

</details>

<details><summary>PyAutoFit profiling bootstrap — needs-decision</summary>

Reviewed 2026-10-04. PyAutoLabs/autofit_profiling does not exist (gh, 2026-10-04). Human decision pending on repo creation; no producer registration until it exists with ported baselines.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoPulse/tree/f1801514ddcf2272b832c2b53713cd2257aea5c0/tasks)

### Active tasks

- [autofit_profiling: bootstrap the repo + general PyAutoFit profiling epic](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/autofit_profiling_bootstrap.md) — needs-decision: Human answers the single repo-creation question (PyAutoLabs/autofit_profiling absent, 2026-10-04) before any porting.

</details>

<details><summary>Critical curves and evaluation grids — needs-decision</summary>

Reviewed 2026-10-04. Release gate met: PyAutoGalaxy#646 first released in 2026.10.4.1. 2026-10-04: /prm of autolens_workspace_test#343 was denied by the auto-mode classifier (&quot;Merge Without Review&quot;); the human runs it outside auto mode to close the evaluation-grid-cap-field task.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/critical_curves.md)

### Active tasks


</details>

<details><summary>Certified positive solver — parked</summary>

Reviewed 2026-10-04. Parked by choice; wiki unchanged since ab1e4fd (2026-09-27). Its three library/workspace Mind drafts remain in Mind. Retain parked; read the project ledger before proposing new work.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/wiki/campaigns/certified_positive_solver.md)

### Active tasks


</details>

## Profiling Results

Choose a project, dataset and model on the interactive board.

[Interactive board](https://pyautolabs.github.io/PyAutoPulse/)

<details><summary>autolens — choose a setup</summary>

[Interactive setup browser](https://pyautolabs.github.io/autolens_profiling/)

<details><summary>cluster</summary>

- **image_plane**: unspecified
- **source_plane**: unspecified

</details>

<details><summary>datacube</summary>

- **delaunay**: alma, alma_high, sma

</details>

<details><summary>experiments</summary>

- **mge**: hst, unspecified

</details>

<details><summary>imaging</summary>

- **delaunay**: ao, euclid, hst, jwst
- **delaunay_matern**: hst
- **delaunay_nn**: hst
- **knn**: hst
- **mge**: ao, euclid, hst, jwst
- **other**: ao, hst, jwst
- **rectangular**: ao, euclid, hst, jwst

</details>

<details><summary>interferometer</summary>

- **delaunay**: alma, alma_high, jvla, sdp81, sma
- **delaunay_hilbert_1500**: alma, sma
- **mge**: alma, alma_high, jvla, sdp81, sma
- **rectangular**: alma, alma_high, jvla, sdp81, sma
- **rectangular_adapt_image_32x32**: alma, sma
- **streaming**: unspecified

</details>

<details><summary>multi_dataset</summary>

- **delaunay**: unspecified
- **mge**: hst

</details>

<details><summary>point_source_image</summary>

- **image_plane**: simple, unspecified

</details>

<details><summary>point_source_source</summary>

- **other**: unspecified
- **source_plane**: simple, unspecified

</details>

</details>

<details><summary>Capture, qualification and legacy diagnostics</summary>


## lens

<!-- pulse:instance name=lens receipt=002238552624370e86b396a65b686691bb4edd23 outcome=ok shown=002238552624370e86b396a65b686691bb4edd23 -->

Project `autolens_profiling`, scope `setup-catalogue`, read from [PyAutoLabs/autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling) `dashboard/catalogue.json` at [`00223855`](https://github.com/PyAutoLabs/autolens_profiling/tree/002238552624370e86b396a65b686691bb4edd23); producer revision `fef5f28d`; generated 2026-10-07T07:00:40Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autolens_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/lens.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · evidence time unknown (evidence unknown (No common measurement wall-clock across legacy evidence; inspect each record.))
- **Qualification:** 0/112 records · 0/0 comparisons qualified

### lens / limitations

- Legacy evidence remains unreviewed; no new baseline has been accepted.
- Source-row isolation prevents cross-file joins where complete configuration identity is unknown.
- The v1 production feed remains published during migration; this is the companion v2 catalogue.
- Indexed-only evidence and static estimates are not successful measurements or measured peak VRAM.
</details>
