Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/feature/autolens_profiling/numba_breakdown_harness_memo_blind.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [PyAutoArray#496](https://github.com/PyAutoLabs/PyAutoArray/issues/496) closed 2026-08-27; no change since the pin. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Next: select one bounded step when prioritised.

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
