Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/bug/workspaces/profile_lens_aggregator_needs_config_dir.md
Migrated-at: 2026-10-03

Original task retained verbatim below. Current scheduling state: `campaigns.yaml`. Historical paths: `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [PyAutoFit#1582](https://github.com/PyAutoLabs/PyAutoFit/issues/1582) closed 2026-09-08; autolens_workspace_developer#133 merged 2026-09-08; developer main still has no root `config/` (aggregator_profiling last touched `e4874fe`).
- Unverified: the bug presumably persists; it was not run.
- Next: select one bounded step when prioritised.


## Check-in 2026-10-13

- Campaign review: #408/#409 merged 2026-10-09. #410 -> #411 -> #412 remain OPEN, lint SUCCESS at reviewed heads ffddf755/a5de4d49/9ce9a132; Mind claims all three awaiting merge. Review flagged statistical/estimator decisions, then human /prm in order. Issue #362 stays open. No new measurement JSON; v2 catalogue remains 0 qualified / 112 records, 0 comparisons.
- Task next step: Unchanged: workspace_developer main still has no root config/ (bug presumed live, not re-run). Select one bounded step when prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.

---

# profile_lens_aggregator.py cannot run from the autolens_workspace_developer root: no config/ directory

Type: bug
Target: autolens_workspace_developer
Repos:
- autolens_workspace_developer
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised
Witness: `python aggregator_profiling/profile_lens_aggregator.py --quick` run from the autolens_workspace_developer root completes without ConfigException.
Unattended: ready
Filed: 2026-09-08

Found while smoke-testing PR autolens_workspace_developer#133 (task aggregator-search-json-sentinel, PyAutoFit#1582).

`aggregator_profiling/mock_lens_results.py:85` calls
`conf.instance.push(new_path="config", output_path=str(root))`, but the repo has no
`config/` directory (tracked or untracked). Run as its docstring instructs, the
script dies immediately with `autonerves.exc.ConfigException: config does not exist`.
A bare `conf.instance.push(new_path="config", ...)` from that root fails identically,
so the fault is the missing config tree, not the script logic. It was added in #218
and can only ever have run from a cwd carrying a config tree. The smoke for #133 was
run from a scratch directory symlinking `autolens_workspace/config`.

Fix options: point `new_path` at the sibling `autolens_workspace/config` via a
resolved path (as other developer scripts do), or vendor a minimal config tree.
