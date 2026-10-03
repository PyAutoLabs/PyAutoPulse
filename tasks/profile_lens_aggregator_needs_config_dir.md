Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/bug/workspaces/profile_lens_aggregator_needs_config_dir.md
Migrated-at: 2026-10-03

Original task retained verbatim below. Current scheduling state: `campaigns.yaml`. Historical paths: `migration.yaml`.

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
