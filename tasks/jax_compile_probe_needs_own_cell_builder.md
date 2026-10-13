Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/maintenance/autolens_profiling/jax_compile_probe_needs_own_cell_builder.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: autolens_profiling#245 closed 2026-09-11; [`scripts/misc/jax_compile/probe.py`](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/scripts/misc/jax_compile/probe.py) still present on main. The Mind source draft was removed in Mind `dbbe5b22` (2026-10-03, move to Pulse); it is not in Mind complete/ or active.md, so this file is the live record.
- Unverified: whether the probe currently runs (not executed).
- Next: select one bounded step when prioritised.


## Check-in 2026-10-13

- Campaign review: #408/#409 merged 2026-10-09. #410 -> #411 -> #412 remain OPEN, lint SUCCESS at reviewed heads ffddf755/a5de4d49/9ce9a132; Mind claims all three awaiting merge. Review flagged statistical/estimator decisions, then human /prm in order. Issue #362 stays open. No new measurement JSON; v2 catalogue remains 0 qualified / 112 records, 0 comparisons.
- Task next step: Unchanged and unissued; scripts/misc/jax_compile/probe.py still on main (run state unverified). Select one bounded step when prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Approved bounded phase — 2026-10-13

- Human approved the HST/MGE current-runtime builder plan in this conversation;
  [implementation issue #413](https://github.com/PyAutoLabs/autolens_profiling/issues/413)
  is active in Mind as `compile-builder-hst-mge`. This supersedes the earlier
  "unissued" next step, without completing the broader domain task.
- The original witness below is incompatible with current evidence: `--cell`
  is not a supported CLI flag, and the retired flat-vector posterior differs
  from the current model-instance-pytree runtime likelihood. Its pinned timings
  cannot validate this restoration. The approved phase instead checks small
  deterministic CPU objective parity and preserves historical results and pins.
- Phase scope: imaging/MGE/HST, fp64, `jit`, existing data only; explicit objective
  identity and isolated output. No gradient/batch/general-cell support, baseline
  acceptance, production measurements or RAL/GPU submissions are authorized.
- Verified locally: tiny CPU compiled/eager objective parity and unsupported-path,
  import, output-isolation and legacy-consumer checks pass. These are implementation
  tests, not campaign measurements. Brain's compile conductor still emits an empty
  dispatch plan because the global builder capability remains unavailable.
- Implementation: [PR #414](https://github.com/PyAutoLabs/autolens_profiling/pull/414),
  head `05c5c49a514db1c3dc2b92d1126cf39d7f4cd68a`, is OPEN, not merged. Shared
  builder [source](https://github.com/PyAutoLabs/autolens_profiling/blob/18b1ee4/scripts/misc/cell_builders/imaging_mge.py)
  and [instrument contract](https://github.com/PyAutoLabs/autolens_profiling/blob/18b1ee4/scripts/misc/jax_compile/README.md)
  were verified 2026-10-13. No production timing was collected.
- Validation: 19 targeted tests; full suite 1,378 passed / 6 skipped, with all 45
  baseline-only failures passing after reverting an inventory-hash-changing route
  description edit. The registry and baseline remain byte-for-byte unchanged.
  Project import smoke, lint, generated catalogue/dashboard and contract checks pass.
  CI is pending at publication; no successful-job inference or scientific acceptance.
- Plan adjustment: partial capability is documented in the instrument and campaign
  journal; the machine-readable global route reason is retained because the baseline
  draft pins the registry's exact bytes. No re-freeze was authorized or performed.
- Next: review and merge the implementation PR when authorized and green, then discuss
  the next bounded experiment and resource request. Broader coverage and compatible
  baselines remain pending. Review date does not refresh measurement freshness.

---

# jax_compile/probe.py lost its cell builder with the searches tier — give profiling its own

Type: maintenance
Target: autolens_profiling
Repos:
- autolens_profiling
Themes:
- jax
- compile
- hygiene
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Consequence: judge
Witness: `python scripts/misc/jax_compile/probe.py --cell <one pinned cell>` runs end to end and reproduces that cell's pinned warm-compile record within its tolerance
Review-minutes: 20
Unattended: ready
Filed: 2026-09-10

`scripts/misc/jax_compile/probe.py` built its cells through `searches._setup.build_for_cell`
(a 2,159-line module of the retired inference programme). autolens_profiling#245 removed
that tier (archived as PyAutoGut ref `archive/condemned/autolens-profiling/inference-programme`
@ `c8b60580`); `build_objective` now raises `NotImplementedError` naming the ref, so the
probe cannot run. Its pinned warm-compile records and the compile dashboard are intact.

Give the probe a builder this repo owns: the runtime/breakdown scripts already construct
every pinned cell (`_production_config.preset_for` + the per-cell model code in
`scripts/imaging/likelihood_runtime/*.py`), so factor the cell construction they share
into a small `scripts/misc/cells.py` (or reuse an existing helper if one exists — survey
first) and point `build_objective` at it. Do not restore anything from the archive ref.
Re-run the probe on every pinned cell and confirm the records still match.

Filed at the close of #245 (scrap-inference-programme); see
`complete/2026/09/autolens-inference-birth.md` for the epic.
