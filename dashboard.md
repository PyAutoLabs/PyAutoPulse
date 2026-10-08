# PyAutoPulse — profiling dashboard

<!-- pulse-campaigns:938f09acacf48ab93bf2de5c0e3ef4f84a61f526f0466765a8e579ca80210082 -->
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

Last check-in: 2026-10-08T06:59:54Z (review date, not measurement freshness).

## Active campaigns

<details><summary>Setup baseline collection and scientific acceptance — needs-decision</summary>

Reviewed 2026-10-07. Specification merged as draft v1 (autolens_profiling#385, 2026-10-06; issue #384 closed). Six unknowns remain: no frozen revisions/env lock; no collection authorization/window; hardware/affinity identity unselected; each cell needs complete settings, input hashes, witness + tolerances; compile per-cell builder unavailable; proposed fp64/mixed coverage is not evidence of support. Human freezes the manifest before separately authorizing collection.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/setup_baseline.md)

### Active tasks

- [Freeze the setup baseline specification, then collect and review evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/setup_baseline_campaign.md) — needs-decision: Specification merged as draft v1 (autolens_profiling#385, 2026-10-06). Human resolves the six recorded unknowns and freezes the specification; collection requires separate compute authorization. The report prepares evidence for human scientific review and never promotes baselines. CPU production arrays use ral only.

</details>

<details><summary>Point-source image plane · CPU — active</summary>

Reviewed 2026-10-07. Phases 1–4 shipped; completion evidence merged (autolens_profiling#373, 2026-10-04). Closing the epic is the human&#x27;s call. Owed leftovers (RAL cleanup, test move, register_model grad-zero prompt, CI smoke cells, constant_folding A/B, nopad deletion, quiet re-runs) are in the Mind draft point_source_cpu_campaign_owed_leftovers.md. RAL leftover folders not re-listed 2026-10-07 (unverified).

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/results/notes/point_source_cpu_campaign.md#campaign-completion-evidence-2026-10-04)

### Active tasks

- [Point-source (single-source) CPU campaign — carried leftovers and completion evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pointsolver_cpu_speed_campaign_remainder.md) — ready: Completion evidence merged (autolens_profiling#373, 2026-10-04). Still owed, via Mind draft draft/maintenance/autolens/point_source_cpu_campaign_owed_leftovers.md: RAL cleanup, test move, register_model grad-zero prompt, CI smoke cells, constant_folding A/B, nopad deletion, quiet re-runs.

</details>

<details><summary>Point-source image plane · A100 — needs-decision</summary>

Reviewed 2026-10-07. Phase 0+1 shipped. Forward-mode gradient NaN (PyAutoLens#767) fixed by PyAutoLens#768 (merged 2026-10-04) and released in 2026.10.7.1 (correctness). Remaining human decision: authorize the autolens_inference image-plane fit measurement. Heart unit-test timing rose on the rewritten #768 test file; not a controlled cost comparison (gradient_cost_probe is the instrument).

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/point_source_gpu_breakdown.md)

### Active tasks

- [Point-source A100 speed-up campaign: profile and optimize with the shared breakdown](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/point_source_image_plane_gpu_breakdown.md) — needs-decision: Forward-mode NaN (PyAutoLens#767) closed: fixed by PyAutoLens#768 (merged 2026-10-04, 0659903d4), released in 2026.10.7.1. The autolens_inference image-plane fit measurement still awaits human authorisation.

</details>

<details><summary>Point-source source plane — parked</summary>

Reviewed 2026-10-07. Core complete; parked. Nautilus leaf autolens_inference#17 merged 2026-10-02; no gradient-sampler leaf yet, so Blackjax stays parked (admission not met). Warm-up task option (a) merged as autolens_profiling#374 (2026-10-04); imaging cells and a release sweep remain.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/point_source_source_plane.md)

### Active tasks

- [Runtime cells&#x27; A100 `single_jit` includes the post-compile warm-up — source-plane 0.642 ms vs a steady 0.267 ms on the same node](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/runtime_cell_single_jit_gpu_warmup.md) — active: Option (a) merged (autolens_profiling#374, 2026-10-04): full_pipeline_single_jit_median_ms (p10/p90) beside unchanged single_jit; GPU headline labelled &quot;first block after compile&quot;. Imaging release-sweep cells not wired. No release sweep on main yet (results/ commits since 2026-10-04: #375 streaming rows, a README refactor), so the new field has no sweep rows.
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

Reviewed 2026-10-07. Decision matrix complete: last cell merged (autolens_profiling#372, 2026-10-04; 1.59e-3 nat CPU/A100 gap accepted by the human). Streaming scaling phase 1 CPU rows merged (#375); 1e8 CPU and A100 rows need compute authorization. fnnls memo back-off released in 2026.10.7.1 (PyAutoArray#615); the #332 after-measurement is owed. Curvature preload and W~ FFT tasks unstarted.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/interferometer_likelihood.md)

### Active tasks

- [Interferometer fixed-mapper searches: reuse the W~ curvature matrix across likelihood calls via `preloads.curvature_matrix`](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_fixed_mapper_curvature_preload.md) — ready: Phase 1 Mind draft (2026-10-04) still unstarted; run it through start_dev. Human science call first - no production SLaM stage holds the mapper fixed today.
- [fnnls warm-start memo: stop it slowing scattered evaluation streams (interferometer CPU, autolens_profiling#332)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_nnls_memo_scattered_stream_guard.md) — active: Library half shipped: PyAutoArray#615 (closes #613) merged 2026-10-06, in 2026.10.7.1. Local solver-only witness (n=576): iid memo on/off 1.49x → 1.17x; walk 0.18x unchanged. Owed: re-run the autolens_profiling#332 ALMA Delaunay 2.17x after-measurement (needs compute authorization).
- [Campaign: interferometer streaming (array-free) vs in-memory — memory and time scaling to 2e8 visibilities](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_streaming_scaling.md) — active: Phase 1 CPU cells + results/streaming_scaling rows merged (autolens_profiling#375, 2026-10-04); wiki/campaigns/interferometer_streaming.md. Optional: 1e8 CPU row and A100 rows (compute authorization). Library candidate unfiled: chunk transformer.image_from in apply_sparse_operator (memory).
- [Interferometer W~ curvature matrix is FFT-bound on the mask extent: pruned padded FFT and real-space pixel scale on the A100](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/interferometer_w_tilde_fft_size_levers.md) — ready: Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.

</details>

<details><summary>Linear-solver accuracy and cost — active</summary>

Reviewed 2026-10-08. Programme question CLOSED by decision 2026-10-08 (decisions/linear-solver-mapper-default-jacobi.md): keep Jacobi as the Mapper default, raw+polish for MGE-only, no library change. Phase 5 merged as autolens_profiling#401 (766f8202; #400 superseded, corpus files out of git with sha256 + regenerate in the manifest, copies on RAL and the laptop); phases 3a/3b/4a merged earlier (#394, #396, #398). Open evidence gaps, not tasks: wide-prior Mapper vectors, an interferometer corpus, the n~1500 CPU batched/unbatched 4e-13 difference, rectangular criterion-2 failures. Campaign stays active for the release re-runs of the solver cells; nothing issued.

[Campaign evidence](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md)

### Active tasks


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

Reviewed 2026-10-08. timing_noise_audit phase 1 (inventory) started 2026-10-08 against autolens_profiling#362 (worktree timing-noise-audit-p1-inventory); related Mind draft call_accounting_ci_timing_threshold.md becomes a fix phase the inventory ranks. Other tasks unchanged and unissued.

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/issues/362)

### Active tasks

- [Audit timing tests and profiling gates for measurement noise](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/timing_noise_audit.md) — active: Phase 1 (inventory, audit only) STARTED 2026-10-08 on the human&#x27;s direction after the linear-solver programme closed: issue autolens_profiling#362 reused (plan comment posted), Mind active/timing_noise_audit_phase1_inventory.md, worktree timing-noise-audit-p1-inventory, Opus executing. Deliverable: results/notes/timing_noise_audit_2026_10.md (inventory + PASS/FAIL/INCONCLUSIVE semantics + fix phases) and a read-only assertion lister. Next: /prm on its PR.
- [MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/mge_likelihood_breakdown_steps_are_cumulative_an.md) — ready: Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.
- [A gradient-cost probe: forward vs `value_and_grad` ms/eval and a strict FD check, on any registry cell](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_cost_probe.md) — ready: Unissued. New context 2026-10-07: Heart unit-test timing flagged PyAutoLens forward-gradient tests +150%/+96% after PyAutoLens#768 rewrote that test file; not a controlled comparison, and this probe is the right instrument. Select one bounded step when prioritised.
- [Numba breakdown harness: perturb the instance so the operated-matrix memo cannot hide a step](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/numba_breakdown_harness_memo_blind.md) — ready: Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.
- [Search settings-estimation + profiling infrastructure (n_starts / batch_size / n_batch)](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/search_settings_estimation_infrastructure.md) — ready: Unchanged and unissued (autolens_profiling#82 closed 2026-08-18). Select one bounded step when prioritised.
- [jax_compile/probe.py lost its cell builder with the searches tier — give profiling its own](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/jax_compile_probe_needs_own_cell_builder.md) — ready: Unchanged and unissued; scripts/misc/jax_compile/probe.py still on main (run state unverified). Select one bounded step when prioritised.
- [profile_lens_aggregator.py cannot run from the autolens_workspace_developer root: no config/ directory](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/profile_lens_aggregator_needs_config_dir.md) — ready: Unchanged: workspace_developer main still has no root config/ (bug presumed live, not re-run). Select one bounded step when prioritised.
- [jax_profiling/gradient/imaging/pixelization.py: 3.2% of its pin move is unattributed](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/gradient_pixelization_pin_residual_drift.md) — ready: Unchanged and unissued (PyAutoArray#490 merged 2026-08-26). Select one bounded step when prioritised.
- [Pair JAX/XLA env vars with measured compile and run times, per backend](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/pair_jax_xla_env_vars_with_measured.md) — ready: Unchanged and unissued. Context: the jax-version policy is now released (2026.10.7.1 libraries require Nerves with the JAX deadlock exclusions). Select one bounded step when prioritised.

</details>

<details><summary>PyAutoFit profiling bootstrap — ready</summary>

Reviewed 2026-10-08. Skeleton merged: autofit_profiling#1 (86c77345, 2026-10-07T21:17Z; AGENTS, hooks, hpc/sync, lint) under search-extensibility B1 (PyAutoMind#492). B1 docs legs PyAutoHeart#292 and .github#34 still open 2026-10-08. Porting unstarted; no producer registration until profiling-summary@2 is published (B4a).

[Campaign evidence](https://github.com/PyAutoLabs/autofit_profiling/pull/1)

### Active tasks

- [autofit_profiling: bootstrap the repo + general PyAutoFit profiling epic](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/tasks/autofit_profiling_bootstrap.md) — ready: Adopted by the search-extensibility epic (Mind draft/research/autofit/search_extensibility_epic.md); skeleton merged as autofit_profiling#1 (2026-10-07T21:17Z) under PyAutoMind#492 (B1). Next is B4a (search.fit breakdown exporter, Pulse fit row, epic-1 bottleneck table), then B4b (EP/graphical baseline port). No producer registration until profiling-summary@2 is published (B4a).

</details>

<details><summary>Critical curves and evaluation grids — needs-decision</summary>

Reviewed 2026-10-07. Phase 3b cap fix shipped: PyAutoGalaxy#646 released in 2026.10.4.1 and autolens_workspace_test#343 merged 2026-10-04. Remaining per the wiki Next line: investigate seed coverage/path completion before cluster engine selection (human picks whether to scope it). Wiki page itself is stale (last edited 2026-10-02, still says #646 open).

[Campaign evidence](https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/critical_curves.md)

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

<!-- pulse:instance name=lens receipt=293d97d689004102c820f07efa7a2185ca5e0d0d outcome=ok shown=293d97d689004102c820f07efa7a2185ca5e0d0d -->

Project `autolens_profiling`, scope `setup-catalogue`, read from [PyAutoLabs/autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling) `dashboard/catalogue.json` at [`293d97d6`](https://github.com/PyAutoLabs/autolens_profiling/tree/293d97d689004102c820f07efa7a2185ca5e0d0d); producer revision `766f8202`; generated 2026-10-08T13:59:51Z; comparison policy `no-temporal-comparisons`. [Project dashboard](https://pyautolabs.github.io/autolens_profiling/) · [receipt](https://github.com/PyAutoLabs/PyAutoPulse/blob/main/receipts/lens.json).

- **Integrity:** ok
- **Freshness:** freshness policy unspecified · evidence time unknown (evidence unknown (No common measurement wall-clock across legacy evidence; inspect each record.))
- **Qualification:** 0/112 records · 0/0 comparisons qualified

### lens / limitations

- Legacy evidence remains unreviewed; no new baseline has been accepted.
- Source-row isolation prevents cross-file joins where complete configuration identity is unknown.
- The v1 production feed remains published during migration; this is the companion v2 catalogue.
- Indexed-only evidence and static estimates are not successful measurements or measured peak VRAM.
</details>


<!-- decision-history:8f1840916151d6a62b1cb1cd473edede0a3647c198fe8ef2371ce31a66c873a5 -->
## Decision History

- <a href="https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/linear-solver-mapper-default-jacobi.md">Keep Jacobi PDIP as the Mapper default and raw+polish as the MGE-only default</a>
