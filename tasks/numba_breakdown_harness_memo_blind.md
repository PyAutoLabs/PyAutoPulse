Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/feature/autolens_profiling/numba_breakdown_harness_memo_blind.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [PyAutoArray#496](https://github.com/PyAutoLabs/PyAutoArray/issues/496) closed 2026-08-27; no change since the pin. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Next: select one bounded step when prioritised.


## Check-in 2026-10-13

- Campaign review: #408/#409 merged 2026-10-09. #410 -> #411 -> #412 remain OPEN, lint SUCCESS at reviewed heads ffddf755/a5de4d49/9ce9a132; Mind claims all three awaiting merge. Review flagged statistical/estimator decisions, then human /prm in order. Issue #362 stays open. No new measurement JSON; v2 catalogue remains 0 qualified / 112 records, 0 comparisons.
- Task next step: Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. Unchanged and unissued (PyAutoArray#496 closed 2026-08-27). Select one bounded step when prioritised.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.

---

# Numba breakdown harness: perturb the instance so the operated-matrix memo cannot hide a step

Type: feature
Target: autolens_profiling
Repos:
- @autolens_profiling
Themes:
- numba-cpu
- profiling
Difficulty: small
Autonomy: safe
Priority: medium
Status: formalised
Consequence: glance
Witness: The `pixelization_numba` and `delaunay_numba` breakdown/runtime harnesses perturb the instance per repeat (or run with `AUTOARRAY_NUMBA_OPERATED_MEMO=0`) and record which in the results JSON `configuration`, keep the pinned log-likelihood check on the unperturbed instance, and the re-baselined euclid + hst rows show the operated-matrix step at its un-memoised cost with the regime change noted in the results README.
Review-minutes: 3
Unattended: ready
Filed: 2026-08-27

## Context (found while measuring PyAutoArray#496, 2026-08-27)

Was a member of the `numba-cpu-likelihood` epic, retired 2026-09-02 to
`complete/archive/epics/numba-cpu-likelihood.md`; it stands alone now.

`scripts/imaging/likelihood_breakdown/pixelization_numba.py` and the
`likelihood_runtime` sibling time `n_repeats=10` evaluations of one fixed
`instance`. Since the cross-evaluation memo in PyAutoArray
`imaging_numba/sparse.py` (sha256 of the pickled linear func), every repeat
after warm-up hits the memo, so "MGE operated mapping matrix (60 funcs)" reads
~0.003 s (euclid) / ~0.01 s (hst) — and `direct_log_likelihood_function_per_call`
is contaminated the same way. Batching the convolution (a 3.7-5.4x win on that
step, measured with `AUTOARRAY_NUMBA_OPERATED_MEMO=0`) showed A/B = 1.04 in the
harness. Real modelling perturbs the MGE parameters every evaluation, so the
memo never hits there.

## Goal

- Per repeat, perturb the instance (e.g. shift the lens-light Gaussian centres
  by 1e-3·k) OR set `AUTOARRAY_NUMBA_OPERATED_MEMO=0` for the numba cells, so
  the step is measured un-memoised; record which in the results JSON
  `configuration`.
- Keep the pinned log-likelihood check on the unperturbed instance.
- Re-baseline the `pixelization_numba` and `delaunay_numba` breakdown/runtime
  results (euclid + hst) and note the regime change in the results README.
