Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autofit/autofit_profiling_bootstrap.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: `gh repo view PyAutoLabs/autofit_profiling` → does not exist; no local checkout. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Human decision still pending: the repo-creation question (Witness). No producer registration until the repo exists with ported baselines.

## Check-in 2026-10-07

- https://github.com/PyAutoLabs/autofit_profiling created 2026-10-07T11:38Z: one Initial commit with LICENSE only, no PRs. The repo-creation question is answered.
- Status → `ready`: porting/bootstrap unstarted; no producer registration until baselines are ported.

## Check-in 2026-10-07 (adopted by search-extensibility)

- Repo created 2026-10-07 (human gate); its lint-green skeleton PR is filed via PyAutoMind#492, phase B1 of the `search-extensibility` epic, which also registers the repo in Mind `repos.yaml` (`fit/autofit_profiling`), Heart `excluded:` and the org profile, and clones it on RAL.
- This task is adopted by the epic: **B4a** = the `search.fit` breakdown exporter, the Pulse `fit` instance row and epic 1's measured bottleneck table; **B4b** = the EP / graphical baseline port. Epic ledger: `PyAutoMind/draft/research/autofit/search_extensibility_epic.md`.
- No producer registration (`registry.yaml` row) until `profiling-summary@2` is published from the repo in B4a.


## Check-in 2026-10-13

- Campaign review: B1 registration is complete: Heart#292 and .github#34 merged 2026-10-08. autofit_profiling main remains skeleton 86c77345: no exporter, harness or measurements, no Pulse fit registration. B4a remains next profiling phase, subject to the search-extensibility epic handoff/review findings; then B4b. Do not restart the separate B3 inference pilot.
- Task next step: B1 registration is complete: Heart#292 and .github#34 merged 2026-10-08. autofit_profiling main remains skeleton 86c77345: no exporter, harness or measurements, no Pulse fit registration. B4a remains next profiling phase, subject to the search-extensibility epic handoff/review findings; then B4b. Do not restart the separate B3 inference pilot.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. B1 registration is complete: Heart#292 and .github#34 merged 2026-10-08. autofit_profiling main remains skeleton 86c77345: no exporter, harness or measurements, no Pulse fit registration. B4a remains next profiling phase, subject to the search-extensibility epic handoff/review findings; then B4b. Do not restart the separate B3 inference pilot.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.

## Check-in 2026-10-14 — B4a at PR; epic-1 ranked table

- B4a implemented (search-extensibility, autofit_profiling#2): [autofit_profiling#3](https://github.com/PyAutoLabs/autofit_profiling/pull/3) adds the `search.fit` breakdown cell `scripts/gaussian_x1/nautilus/search_fit_breakdown.py` (re-homed from autofit_workspace_developer `searches_minimal/nautilus_profile.py`), its committed rows, the `profiling-summary@2` exporter (`dashboard/catalogue.json`, validated by this organ's reader) and the Pages + `pulse-refresh` workflow. This Pulse PR registers instance `fit`; the developer-workspace originals are retired in a separate PR. Merge order: autofit_profiling#3 → this PR (after its Pages deploy is live and the `fit` receipt is captured) → autofit_workspace_developer.
- Reproduction: the bare-sampler re-run matches the 2026-07 findings within the cell's ±10 pp gate (NN training 53.8 % vs 51.7 %, bound geometry 25.3 % vs 25.2 %, likelihood 11.6 % vs 14.3 %; log Z −57.455 both).
- Measurements are producer declarations (`validation: unreviewed`); the Brain's profiling conductor judges them. Laptop CPU only; no RAL compute.

### Epic 1 — ranked bottleneck table, one `search.fit` on a fast likelihood

`af.Nautilus(n_live=200, n_networks=4, seed=1, number_of_cores=1).fit` on gaussian_x1 (3 parameters, 100 pixels), numpy fp64, laptop CPU (WSL2, 8 cores), PyAutoFit `911fe05e1`, nautilus 1.0.5; median of 3 fresh fits, wall 28.4 s, 7 501 likelihood calls; exclusive component wall. Evidence: [`results/gaussian_x1/nautilus/breakdown.json`](https://github.com/PyAutoLabs/autofit_profiling/blob/9074c7c/results/gaussian_x1/nautilus/breakdown.json); full page: [`wiki/campaigns/search_fit_bottlenecks.md`](https://github.com/PyAutoLabs/autofit_profiling/blob/9074c7c/wiki/campaigns/search_fit_bottlenecks.md).

| rank | component | owner | share of wall |
|---:|---|---|---:|
| 1 | NN ensemble training | nautilus | 43.4 % |
| 2 | checkpoint I/O (103 HDF5 writes) | nautilus, switched on by PyAutoFit's `filepath=checkpoint.hdf5` | 24.5 % |
| 3 | bound geometry | nautilus | 20.4 % |
| 4 | visualisation | PyAutoFit | 4.1 % |
| 5 | sampler bookkeeping | nautilus | 2.3 % |
| 6 | samples output (pre/post-fit, samples, latents, summary) | PyAutoFit | 1.7 % |
| 7 | likelihood (prior transform + `Fitness`) | PyAutoFit + user | 1.1 % |
| 8 | other (unattributed remainder) | PyAutoFit | 1.0 % |
| 9 | proposal sampling | nautilus | 0.8 % |

`likelihood_share` from the B2/B3 rows (autofit_inference `dashboard/summary.json` at [`637713b2`](https://github.com/PyAutoLabs/autofit_inference/blob/637713b253ab149f87a08ea0b02fcb009b4aa24e/dashboard/summary.json); `catalogue/search_catalogue.json` carries no such field): Nautilus numpy median 1.9 % (n=11, gaussian_x3), Nautilus JAX CPU ≈0.01 % (n=12), Dynesty numpy 26–33 %, Dynesty JAX CPU 2.5–4.5 %. On a fast likelihood a Nautilus `search.fit` is ~98 % search and wrapper overhead; the one PyAutoFit-side lever above 5 % is the per-update nautilus checkpoint write.

- Next: B4b (EP / graphical baseline port). Epic 2 (EP loop) is **not** opened; it waits for epic 1's top findings to ship. Candidate one-PR prompts (checkpoint cadence, end-of-fit visualisation) are listed in the project page for the human / profiling conductor, not filed.


## Check-in 2026-10-14 — B4b at PR; EP / graphical baselines reproduced

- B4b (search-extensibility, issue autofit_profiling#4) ports `autofit_workspace_developer/{ep,graphical}` as `scripts/gaussian_1d_ep/{ep,graphical}/baseline.py` and adds `scripts/analytic_gaussian/parity/benchmark.py`, which runs autofit_workspace_test's analytic parity script unchanged. Each row exports a `runtime` wall and a `memory` `host_peak_rss` record on the existing axes (sibling result schemas `autofit-profiling-baseline` / `-parity`; no registry row, no contract bump). Findings: `wiki/campaigns/ep_graphical_baselines.md` in autofit_profiling.
- Host pin (decided and flagged): the same laptop as B4a (`DESKTOP-H143S82`, WSL2), not the release-sweep A100 node, so Pulse's same-host rule pairs the new records with B4a's. PyAutoFit `df6d218f1`, JAX CPU float64.
- Reproduction against the committed developer `baseline.json`: every `truth_log_likelihood_sum` matches exactly and both N30 sanity FAILs reproduce (graphical: max-logL rule; EP: shared centre |z| 6.7). Every wall is faster beyond the `runtime-drift-2x-1ms` policy (graphical 6.0 / 7.1 / 19.0 s vs 22.8 / 50.7 / 132.8 s; EP 37.1 / 152.9 / 842.8 s vs 251.9 / 566.9 / 1758.7 s; all `improved`), so the "N3/N10 within 2x" witness is not met as written; the committed baselines predate the changes behind the developer postfix re-runs. Another session shared the host during the runs (load 2.5–4.7), so the seconds are conservative.
- Analytic parity (seed 0, N = 5): PARITY PASS 41/41 for closed form vs minimal EP vs graphical vs EP; closed-form `sigma_q95` 12.1536 matches the banked 12.15; `analytic_gaussian_priors.py` recorded as parked NEEDS_FIX, not run.
- This Pulse branch refreshes the fixture; the `fit` receipt and snapshot are refreshed here after the autofit_profiling PR merges and its Pages deploy is live. Measurements are `unreviewed`; the Brain's profiling conductor judges.

---

# autofit_profiling: bootstrap the repo + general PyAutoFit profiling epic

Type: research
Target: PyAutoFit
Repos:
- PyAutoFit
- autofit_profiling
Themes:
- profiling
- graphical-ep
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised
Consequence: glance
Witness: The `autofit_profiling` repo exists (created only after the human's interactive confirmation) with the ported `ep/`, `graphical/` and analytic-benchmark packages reproducing their committed baseline numbers, and epic 1's issue is open with a measured, ranked bottleneck table for a single `search.fit` on a fast likelihood; epic 2 is not opened.
Review-minutes: 3
Unattended: ready
Campaign: research/graphical_ep/ep_campaign.md (Phase 6)
Filed: 2026-08-19 (backfilled from git)

## Why

For the IC50 and cosmology use cases the individual Factor fits will end up
fast; the bottleneck becomes PyAutoFit itself — wrapping up a fit on one
factor, writing its output, starting the next, building the cavity
distributions. The 2026-07 scoping baselines already show this shape: EP is
~11× slower than graphical at every N, with per-factor visualisation alone at
~48% of EP runtime and `scipy.stats.truncnorm` prior transforms at 25–38%
(`research/graphical_ep/ep_scoping.md`, `graphical_scoping.md`). Slowdowns in
`non_linear/` (priors, paths, output) accumulate per factor fit and *become*
the EP bottleneck — so PyAutoFit needs a general profiling assessment, not
just an EP one.

## Deliverable 1 — the `autofit_profiling` repo

A new GitHub repo mirroring `autolens_profiling`'s responsibility, but for
all things PyAutoFit. **Repo creation is human-gated: confirm interactively
with James before creating anything on GitHub.** Seed it by porting the
existing baseline packages from `autofit_workspace_developer/` (`ep/`,
`graphical/`, and the analytic benchmark, shipped 2026-09-02 as
`complete/2026/09/analytic-gaussian-benchmark.md`) so results,
harnesses and hotspot files live in one place with committed history, the way
autolens_profiling does for likelihoods.

## Deliverable 2 — two epics, sequenced (created at start_dev time, one at a
time — never bulk-issued)

1. **General PyAutoFit profiling** (first): a full profiling assessment of a
   single `search.fit` — prior transforms, `non_linear` wrapper overhead
   (paths setup, samples-to-CSV, visualisation, latent samples,
   search-internal cleanup), output I/O — on a fast likelihood so the
   overhead has nowhere to hide. Ranked findings filed as one-PR prompts.
2. **EP-loop profiling** (second, follows on): the EP-specific overhead —
   cavity construction, message updates, `factor_graph.optimise`
   orchestration — building directly on the ranked sub-task list already in
   `ep_scoping.md` (viz suppression, truncnorm fast path, folder-cleanup
   skip, orchestration cProfile, parallel local fits, sampler reuse). Most
   per-fit wins from epic 1 multiply by M·N under EP, which is why epic 1
   lands first.

## Acceptance

- Repo exists with the ported baselines reproducing their committed numbers.
- Epic 1 issue open with a measured, ranked bottleneck table for a single
  search.fit; epic 2 issue opened only after epic 1's top findings ship.
