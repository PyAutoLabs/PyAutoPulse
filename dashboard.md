# PyAutoPulse — profiling dashboard

<!-- pulse-campaigns:40ebeabfcfa2bcc9dccff22b0816ae55956895694c0126147309ac3c6d3a7460 -->
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

Last check-in: 2026-10-13T17:51:40Z (review date, not measurement freshness).

## Active campaigns

<details><summary>Setup baseline collection and scientific acceptance — needs-decision</summary>

Reviewed 2026-10-13. Review the Pulse collection choices (candidate input hashes and 31-worker resource plan verified without execution) alongside project correctness audit #417. Resolve data origin/suitability, named host/stack/full settings, witness/tolerances and background-load method. No freeze, compute or acceptance authorized.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/pull/416)

### Active tasks

- [Freeze the setup baseline specification, then collect and review evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/setup_baseline_campaign.md) — needs-decision: HST/MGE raw fixed-parameter CPU runner merged in #416; Pulse handoff #55 merged and Mind implementation closed. Resolve exact production host/stack/data, full settings, independent correctness witness/tolerances and background-load method. No collection, campaign freeze or acceptance authorized; global compile dispatch remains unavailable.
- [Prepare and review the HST/MGE fp64 CPU pilot](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/hst_mge_cpu_pilot.md) — needs-decision: Review the Pulse collection choices (candidate input hashes and 31-worker resource plan verified without execution) alongside project correctness audit #417. Resolve data origin/suitability, named host/stack/full settings, witness/tolerances and background-load method. No freeze, compute or acceptance authorized.

</details>

<details><summary>Point-source image plane · CPU — active</summary>

Reviewed 2026-10-13. No new committed campaign measurements. Phases 1–4 remain shipped; epic closure is a human decision. Carried leftovers remain pending. RAL queue empty at review, but transfer preview timed out: cleanup folders and unpulled results unverified. Select one owed cleanup/measurement phase only after review.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/results/notes/point_source_cpu_campaign.md#campaign-completion-evidence-2026-10-04)

### Active tasks

- [Point-source (single-source) CPU campaign — carried leftovers and completion evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pointsolver_cpu_speed_campaign_remainder.md) — ready: No new committed campaign measurements. Phases 1–4 remain shipped; epic closure is a human decision. Carried leftovers remain pending. RAL queue empty at review, but transfer preview timed out: cleanup folders and unpulled results unverified. Select one owed cleanup/measurement phase only after review.

</details>

<details><summary>Point-source image plane · A100 — needs-decision</summary>

Reviewed 2026-10-13. No new image-plane fit measurement found. Correctness fix #768 remains shipped; current libraries now have release 2026.10.12.1, not a measured performance baseline. Image-plane admission measurement still needs authorization. #411 merged 2026-10-13, recording the paired-round MDI reinterpretation; no new measurement.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/point_source_gpu_breakdown.md)

### Active tasks

- [Point-source A100 speed-up campaign: profile and optimize with the shared breakdown](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_image_plane_gpu_breakdown.md) — needs-decision: No new image-plane fit measurement found. Correctness fix #768 remains shipped; current libraries now have release 2026.10.12.1, not a measured performance baseline. Image-plane admission measurement still needs authorization. #411 merged 2026-10-13, recording the paired-round MDI reinterpretation; no new measurement.

</details>

<details><summary>Point-source source plane — parked</summary>

Reviewed 2026-10-13. Core remains parked; autolens_inference#21 reorganized setup evidence but added no point-source gradient admission measurement. #408 merged median fields into 11 runtime cells; #412 merged 2026-10-13, completing headline/repeat support. No new runtime sweep; keep Blackjax parked.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/point_source_source_plane.md)

### Active tasks

- [Runtime cells&#x27; A100 `single_jit` includes the post-compile warm-up — source-plane 0.642 ms vs a steady 0.267 ms on the same node](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/runtime_cell_single_jit_gpu_warmup.md) — active: #408 merged 2026-10-09: median headline fields now wired into 11 runtime cells, superseding the old imaging-not-wired note. #412 merged 2026-10-13 with remaining headline/repeat support. No new runtime sweep; fresh median evidence still missing.
- [Point-source source-plane chi-squared speed-up campaign — remaining candidates (phases 1–2e shipped)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_source_plane_chi_squared_speed.md) — blocked: Still blocked on a point-source gradient-sampler admission measurement. Inference #21 is setup organization, not that measurement. Keep parked.

</details>

<details><summary>Cluster PointSolver robustness and performance — active</summary>

Reviewed 2026-10-13. No campaign wiki/results change or new matching implementation claim found. Representative cluster baseline and observable-overflow policy remain unstarted. Choose one bounded phase; inherited single-source results do not qualify a representative cluster baseline.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/cluster_pointsolver.md)

### Active tasks

- [Cluster PointSolver — robustness, analysis settings and performance](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/cluster_pointsolver_speed.md) — ready: Unissued, no claim. Pick one bounded phase per Mind epics.md: observable-overflow invalid-result policy + CI witness, or a representative-data baseline cell.
- [PointSolver profiling cells: lensed quasar → cluster runtime tier → single/multi-source → multiplane](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_solver_profiling_cells.md) — ready: Unissued, no claim. Candidate first cell: a representative-data cluster likelihood_runtime baseline (single-source preset).

</details>

<details><summary>Interferometer likelihood and streaming — active</summary>

Reviewed 2026-10-13. No new committed measurements. Decision matrix remains filled; streaming 1e8 CPU/A100 rows and the #332 memo after-measurement still need authorization. #411 merged 2026-10-13: the historical numba kill gate is INCONCLUSIVE (four rounds). Curvature preload needs the fixed-mapper science decision; FFT levers remain unstarted.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/interferometer_likelihood.md)

### Active tasks

- [Interferometer fixed-mapper searches: reuse the W~ curvature matrix across likelihood calls via `preloads.curvature_matrix`](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_fixed_mapper_curvature_preload.md) — ready: Phase 1 Mind draft (2026-10-04) still unstarted; run it through start_dev. Human science call first - no production SLaM stage holds the mapper fixed today.
- [fnnls warm-start memo: stop it slowing scattered evaluation streams (interferometer CPU, autolens_profiling#332)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_nnls_memo_scattered_stream_guard.md) — active: Library half shipped: PyAutoArray#615 (closes #613) merged 2026-10-06, in 2026.10.7.1. Local solver-only witness (n=576): iid memo on/off 1.49x → 1.17x; walk 0.18x unchanged. Owed: re-run the autolens_profiling#332 ALMA Delaunay 2.17x after-measurement (needs compute authorization).
- [Campaign: interferometer streaming (array-free) vs in-memory — memory and time scaling to 2e8 visibilities](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_streaming_scaling.md) — active: Phase 1 CPU cells + results/streaming_scaling rows merged (autolens_profiling#375, 2026-10-04); wiki/campaigns/interferometer_streaming.md. Optional: 1e8 CPU row and A100 rows (compute authorization). Library candidate unfiled: chunk transformer.image_from in apply_sparse_operator (memory).
- [Interferometer W~ curvature matrix is FFT-bound on the mask extent: pruned padded FFT and real-space pixel scale on the A100](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_w_tilde_fft_size_levers.md) — ready: Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.

</details>

<details><summary>Linear-solver accuracy and cost — active</summary>

Reviewed 2026-10-13. Retain the 2026-10-08 human decision: Jacobi for Mapper, raw+polish for MGE-only, no default change. Project wiki still says decision pending (stale). No new solver measurements after the recorded phase-5 results; release 2026.10.12.1 does not supply a rerun. Wide-prior/interferometer gaps remain evidence gaps, not authorized tasks.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md)

### Active tasks


</details>

<details><summary>Production imaging and likelihood breakdown — active</summary>

Reviewed 2026-10-13. No new production-over-sampling or post-certified measurements. #408 now adds median headline fields to runtime cells; #412 merged 2026-10-13 and extends remaining headline surfaces. Production presets, memo-blind harness, cumulative MGE steps and quick-update costs remain separate pending work. Scope production-preset phase 1 (CPU smoke only); A100 measurement separately authorized.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/post_certified_breakdown.md)

### Active tasks

- [Profile imaging pixelizations at production over-sampling](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/imaging_production_over_sampling.md) — ready: Phase 1 (workspace-only): --instrument euclid\|hst presets for the JAX Delaunay runtime/breakdown cells, keeping flat-1 selectable; CPU smoke only. A100 re-measure is a separate compute-authorized phase.
- [Assess remaining likelihood bottlenecks after certified solver integration on CPU and GPUs](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/post_certified_solver_likelihood_breakdown.md) — needs-slicing: Blocked-by is stale: resolved 2026-09-27 (PyAutoArray#567 in 2026.9.26.1). Unissued; scope one bounded phase from the full task contract.
- [Quick-update plotting cost — minutes per update, and it is not JAX compile](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/quick_update_plotting_cost.md) — ready: Unchanged; targets PyAutoLens/PyAutoGalaxy (PyAutoLens#680 closed 2026-07-31, no follow-up issue). Select one bounded step when prioritised.

</details>

<details><summary>Measurement reliability and profiling tools — active</summary>

Reviewed 2026-10-13. Timing audit #410–#412 and raw HST/MGE pilot producer #416 merged; implementation issues #362/#415 closed. No fresh production measurements or scientific acceptance. C1/C11 repeat counts, C5 estimator policy, memo interpretation, fresh runtime repeats and other tools remain pending.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/pull/416)

### Active tasks

- [MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/mge_likelihood_breakdown_steps_are_cumulative_an.md) — ready: Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.
- [A gradient-cost probe: forward vs `value_and_grad` ms/eval and a strict FD check, on any registry cell](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_cost_probe.md) — ready: Unissued. New context 2026-10-07: Heart unit-test timing flagged PyAutoLens forward-gradient tests +150%/+96% after PyAutoLens#768 rewrote that test file; not a controlled comparison, and this probe is the right instrument. Select one bounded step when prioritised.
- [Numba breakdown harness: perturb the instance so the operated-matrix memo cannot hide a step](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/numba_breakdown_harness_memo_blind.md) — ready: Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.
- [Search settings-estimation + profiling infrastructure (n_starts / batch_size / n_batch)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/search_settings_estimation_infrastructure.md) — ready: Unchanged and unissued (autolens_profiling#82 closed 2026-08-18). Select one bounded step when prioritised.
- [jax_compile/probe.py lost its cell builder with the searches tier — give profiling its own](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/jax_compile_probe_needs_own_cell_builder.md) — active: Manual HST/MGE fp64 jit builder #414 and separate raw pilot runner #416 merged. Bounded Mind implementations complete; wider builder coverage/global compile dispatch still unavailable. Agree a next capability or separately authorize a qualified pilot; no production compute authorized.
- [profile_lens_aggregator.py cannot run from the autolens_workspace_developer root: no config/ directory](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/profile_lens_aggregator_needs_config_dir.md) — ready: Unchanged: workspace_developer main still has no root config/ (bug presumed live, not re-run). Select one bounded step when prioritised.
- [jax_profiling/gradient/imaging/pixelization.py: 3.2% of its pin move is unattributed](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_pixelization_pin_residual_drift.md) — ready: Unchanged and unissued (PyAutoArray#490 merged 2026-08-26). Select one bounded step when prioritised.
- [Pair JAX/XLA env vars with measured compile and run times, per backend](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pair_jax_xla_env_vars_with_measured.md) — ready: Unchanged and unissued. Context: the jax-version policy is now released (2026.10.7.1 libraries require Nerves with the JAX deadlock exclusions). Select one bounded step when prioritised.

</details>

<details><summary>PyAutoFit profiling bootstrap — active</summary>

Reviewed 2026-10-14. B4a at PR; B4b next. B4a = autofit_profiling#3 (search.fit breakdown cell, profiling-summary@2 exporter, Pages) then this Pulse fit row, then the autofit_workspace_developer retirement PR, merged in that order. Epic-1 ranked table filed in tasks/autofit_profiling_bootstrap.md (2026-10-14); epic 2 not opened. B4b = the EP / graphical baseline port.

[Campaign evidence](https://github.com/PyAutoLabs/autofit_profiling/pull/3)

### Active tasks

- [autofit_profiling: bootstrap the repo + general PyAutoFit profiling epic](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/autofit_profiling_bootstrap.md) — active: B4a at PR; B4b next. B4a = autofit_profiling#3 (search.fit breakdown cell, profiling-summary@2 exporter, Pages) then this Pulse fit row, then the autofit_workspace_developer retirement PR, merged in that order. Epic-1 ranked table filed in tasks/autofit_profiling_bootstrap.md (2026-10-14); epic 2 not opened. B4b = the EP / graphical baseline port.

</details>

<details><summary>Critical curves and evaluation grids — needs-decision</summary>

Reviewed 2026-10-13. No new campaign measurement. Phase 3b cap fix remains shipped; project wiki still incorrectly says #646 awaits merge/release. Seed coverage and path completion remain unresolved; retain marching-squares decision and ask the human whether to scope the next phase.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/critical_curves.md)

### Active tasks


</details>

<details><summary>Certified positive solver — parked</summary>

Reviewed 2026-10-13. Parked unchanged. No new campaign evidence; existing C2/library/workspace drafts remain pending. Do not infer admission from solver timing, and do not change default or restart the campaign.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/certified_positive_solver.md)

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

<!-- pulse:instance name=lens receipt=e4266a1355a860d2274a82722858349cd3521e46 outcome=ok shown=e4266a1355a860d2274a82722858349cd3521e46 -->

Project `autolens_profiling`, scope `setup-catalogue`, read from [PyAutoLabs/autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling) `dashboard/catalogue.json` at [`e4266a13`](https://github.com/PyAutoLabs/autolens_profiling/tree/e4266a1355a860d2274a82722858349cd3521e46); producer revision `b5b8160b`; generated 2026-10-13T17:24:03Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autolens_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/lens.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · evidence time unknown (evidence unknown (No common measurement wall-clock across legacy evidence; inspect each record.))
- **Qualification:** 0/112 records · 0/0 comparisons qualified

### lens / limitations

- Legacy evidence remains unreviewed; no new baseline has been accepted.
- Source-row isolation prevents cross-file joins where complete configuration identity is unknown.
- The v1 production feed remains published during migration; this is the companion v2 catalogue.
- Indexed-only evidence and static estimates are not successful measurements or measured peak VRAM.
</details>

<details><summary>autofit — choose a setup</summary>

[Interactive setup browser](https://pyautolabs.github.io/autofit_profiling/)

<details><summary>gaussian_x1</summary>

- **gaussian**: unspecified

</details>

</details>

<details><summary>Capture, qualification and legacy diagnostics</summary>


## fit

<!-- pulse:instance name=fit receipt=007791a6fa7ac7ddea3b1fae666de46d82a797eb outcome=ok shown=007791a6fa7ac7ddea3b1fae666de46d82a797eb -->

Project `autofit_profiling`, scope `search-fit-breakdown`, read from [PyAutoLabs/autofit_profiling](https://github.com/PyAutoLabs/autofit_profiling) `dashboard/catalogue.json` at [`007791a6`](https://github.com/PyAutoLabs/autofit_profiling/tree/007791a6fa7ac7ddea3b1fae666de46d82a797eb); producer revision `—`; generated 2026-10-14T09:19:45Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autofit_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/fit.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · age 0 d at fetch 2026-10-14 (evidence 2026-10-14)
- **Qualification:** 17/17 records · 0/0 comparisons qualified

### fit / limitations

- Laptop CPU only (single host, WSL2); wall times vary up to ±40 % between sessions, so shares are the comparable quantity, not seconds.
- Component times are exclusive monkey-patched wall-clock intervals; 'other' is wall minus the instrumented total, not a measured phase.
- Every record is unreviewed: the producer declares measurements, the Brain's profiling conductor judges them; nothing here is a verdict.
- No temporal comparisons yet: one baseline per setup, no drift policy.
</details>


<!-- decision-history:8f1840916151d6a62b1cb1cd473edede0a3647c198fe8ef2371ce31a66c873a5 -->
## Decision History

- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md">Keep Jacobi PDIP as the Mapper default and raw+polish as the MGE-only default</a>
