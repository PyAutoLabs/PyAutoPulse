Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autolens_profiling/interferometer_decision_matrix_last_cell.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: RAL `sacct -j 375978` shows `375978_3 COMPLETED 01:11:36 0:0` on euclid-ral-gpu-1; `error.375978_3.err` has 0 Traceback and 0 RESOURCE_EXHAUSTED.
- VERIFIED: `results/breakdown/interferometer/alma_high/pixelization_numba_hpc_ral_cpu_fp64_r5.0.{json,png}` exist under `/mnt/ral/jnightin/autolens_profiling_wt/interferometer-decision-matrix/` (Sep 30 21:44) and are absent from autolens_profiling origin/main `a93f37a`. The JSON reports `inversion_path == InversionInterferometerSparseNumba` and `numba_vs_numpy_fft_max_abs_nats = 7.45e-09`.
- Witness not met as read: the CPU `log_evidence` (-60244101.501766354) and the A100 row's `figure_of_merit` (-60244101.503356226, [on main](https://github.com/PyAutoLabs/autolens_profiling/blob/a93f37a7ade16fcb7673a7777dfde505183728ed/results/breakdown/interferometer/alma_high/pixelization_hpc_a100_fp64_r5.0.json)) differ by ~1.59e-3 nat (subtraction of the two reported log-evidences, by the survey agent), above the ≤1e-3 nat bar. The A100 row predates PyAutoArray#595 (Array `9428eca2`, pdip); cause attribution unverified.
- Unverified/unavailable: float32-truncation grep of the error log; RAL mirror revisions.
- Human decision: accept the gap as the r3.5 cell did (alma_high r3.5 rect misses at 1.5e-3 nat, wiki journal 2026-09-30), or re-run the A100 row on post-#595 revisions. Then steps 1–5 (commit the row, fill note and index; no compute). Step 6 RAL cleanup of both dirs (still present) also needs the human's go-ahead.

---

# Interferometer decision matrix — fill the last cell (CPU rect 39² at alma_high r5.0) and flip the wiki row to shipped

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Themes:
- interferometer
- numba-cpu
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft
Consequence: glance
Witness: `results/breakdown/interferometer/alma_high/pixelization_numba_hpc_ral_cpu_fp64_r5.0.json` is committed. Its gated arm has `configuration.inversion_path == InversionInterferometerSparseNumba`. Numba vs FFT agree to ≤ 0.5 nat, and CPU vs A100 (the 198.6 ms A100 row) agree to ≤ 1e-3 nat. The note's rect alma_high r5.0 row no longer reads "pending".
Review-minutes: 4
Unattended: needs-human
Lane: local-dev
Epic: interferometer-likelihood-campaign
Filed: 2026-09-30

## Context

- Status: split out of `interferometer-decision-matrix` at close-out. Phase 4 shipped 13 of 14 cells in
  `complete/2026/09/interferometer-decision-matrix.md` (autolens_profiling#358, merge `227b5c91`), and this
  is what remains.
- The campaign map is retired at `complete/archive/epics/interferometer_likelihood_campaign.md`.
- The CPU rect 39² cell at alma_high r5.0 (RAL job **375978_3**) was still RUNNING at merge. The note
  `results/notes/interferometer_likelihood_decision_matrix_2026_09.md` marks it "pending".

## What

1. **Pull.** Job 375978_3 writes `alma_high/pixelization_numba_hpc_ral_cpu_fp64_r5.0.{json,png}` into
   `/mnt/ral/jnightin/autolens_profiling_wt/interferometer-decision-matrix/results/breakdown/interferometer/`.
   Check `sacct -j 375978_3` reads COMPLETED and that the `.err` has 0 Tracebacks. Then copy both files into
   `results/breakdown/interferometer/alma_high/` in a fresh task worktree off main.
2. **Verify** before quoting a number:
   - the gated arm's `configuration.inversion_path` is `InversionInterferometerSparseNumba`;
   - numba vs NumPy FFT log-evidence agrees to ≤ 0.5 nat;
   - CPU vs A100 agrees to ≤ 1e-3 nat against the existing A100 rect alma_high r5.0 row (198.6 ms);
   - `source_revisions` match the private clone SHAs recorded in the note (Nerves 1ec1c82, Fit b13169e2,
     Array 7a89e19a, Galaxy 4c834ced, Lens efd13c4c).
3. **Fill the note.** Update the rect alma_high r5.0 row, the status line and the blocked-cells table in
   `results/notes/interferometer_likelihood_decision_matrix_2026_09.md`. Recheck rule 4's 43–114× alma_high
   range against the new row. Mark 375978_3 COMPLETED with its wall time in the RAL jobs line.
4. **Flip `wiki/index.md`.** The interferometer campaign row should read shipped (phase 4 merged, all cells
   filled). If the campaign page's Phase-4 section also says "pending", update it too.
5. **Regenerate** `build_readme.py` and `build_dashboard.py` (and run each with `--check`), then run the repo lint
   (check_wiki, check_results_layout, check_submits, ruff, pytest). Open one small PR.
6. **Afterwards** (after merge, at close-out): remove the RAL worktree
   `/mnt/ral/jnightin/autolens_profiling_wt/interferometer-decision-matrix` and the private library clone
   `/mnt/ral/jnightin/PyAuto_branch/interferometer-decision-matrix`, but only once no job of this campaign
   is running from them (`squeue -u jnightin`).

## Done when

- The JSON + PNG are committed, the note row is filled and verified, `wiki/index.md` reads shipped, the READMEs and
  dashboard are regenerated, and lint is green on a merged PR.
- The RAL worktree and private library clone are removed.
