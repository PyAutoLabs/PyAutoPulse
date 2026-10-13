Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/bug/workspaces/mge_likelihood_breakdown_steps_are_cumulative_an.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: no GitHub refs; no change since the pin. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Next: select one bounded step when prioritised.


## Check-in 2026-10-13

- Campaign review: #408/#409 merged 2026-10-09. #410 -> #411 -> #412 remain OPEN, lint SUCCESS at reviewed heads ffddf755/a5de4d49/9ce9a132; Mind claims all three awaiting merge. Review flagged statistical/estimator decisions, then human /prm in order. Issue #362 stays open. No new measurement JSON; v2 catalogue remains 0 qualified / 112 records, 0 comparisons.
- Task next step: Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. Unchanged and unissued (no GitHub refs, 2026-10-04). Select one bounded step when measurement-tools is prioritised.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.

---

# MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0

Type: bug
Target: workspaces
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: safe
Priority: low
Memory: wiki/galaxies/sources/massive-ellipticals.md; wiki/lensing/sources/dark-matter-substructure.md; reading-queue.md
Status: formalised
Consequence: glance
Witness: After the fix, `likelihood_breakdown/mge.py` on the HST cell writes a JSON whose step timings sum to within 15% of the fused `likelihood_runtime/mge.py` single-call time (currently 40 ms vs 29.6 ms), and `configuration.linear_gaussians` equals the number of linear Gaussians inside the Basis objects (40 for the profiling cell), in both breakdown and runtime JSONs.
Review-minutes: 3
Unattended: ready

# MGE likelihood_breakdown steps are cumulative and `linear_gaussians` is reported as 0

Type: bug
Priority: low
Target: autolens_profiling
Witness: After the fix, `likelihood_breakdown/mge.py` on the HST cell writes a JSON whose step timings sum to within 15% of the fused `likelihood_runtime/mge.py` single-call time (currently 40 ms vs 29.6 ms), and `configuration.linear_gaussians` equals the number of linear Gaussians inside the Basis objects (40 for the profiling cell), in both breakdown and runtime JSONs.


Found in the 2026-09-24 MGE likelihood audit.

1. `scripts/imaging/likelihood_breakdown/mge.py`: step 2 (`mapping_matrix_from_params`, ~:418) re-runs the ray-trace and step 3 (`blurred_mm_from_params`, ~:462) rebuilds steps 1-2, so the per-step timings are cumulative and `total_step_by_step` double-counts. The published `mge_breakdown_hst_v2026.8.17.1.json` says 40.3 ms; the fused runtime is ~29.6 ms, and the real step-sum is ~29 ms (blurred 25.6 + D/F/NNLS/image/chi2 3.4). The A100 `mge_hpc_a100_fd64.json` total 7.8 ms is really ~6.5 ms, which makes NNLS ~44% of an A100 evaluation, not 36%. Check whether the other breakdown scripts (pixelization.py, delaunay*.py, fixed_light*.py) share the pattern before fixing only mge.py.
2. `tracer.cls_list_from(cls=al.lp_linear.LightProfileLinear)` (breakdown/mge.py ~:311, likelihood_runtime/mge.py ~:332) does not look inside an MGE `Basis`, so both scripts write `configuration.linear_gaussians: 0`; the real counts are 40 (profiling cell). Count the linear profiles inside each Basis.
3. Fix both, regenerate the affected result JSONs/PNGs and the README dashboards (`build_readme.py --check` gates lint), and note in the JSON/README that pre-fix breakdown totals are cumulative and not comparable.

<!-- formalised by the Intake (Conception) Agent on 2026-09-24 from file:/tmp/claude-1000/-home-jammy-Code-PyAutoLabs/4c46534e-38b6-47fd-9021-8040da7c7d92/scratchpad/mge_audit/prompt_breakdown.md -->
