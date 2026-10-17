Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autolens_profiling/interferometer_w_tilde_fft_size_levers.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED 2026-10-04: no PR, issue, branch or results on GitHub; unstarted. No Mind active claim.
- Next: select one bounded step when the interferometer campaign prioritises it.


## Check-in 2026-10-13

- Campaign review: No new committed measurements. Decision matrix remains filled; streaming 1e8 CPU/A100 rows and the #332 memo after-measurement still need authorization. #411 proposes making the historical numba kill gate INCONCLUSIVE (four rounds); it is unmerged. Curvature preload needs the fixed-mapper science decision; FFT levers remain unstarted.
- Task next step: Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.
- Evidence: [project main reviewed at 4db4d988](https://github.com/PyAutoLabs/autolens_profiling/blob/4db4d988e520a82219152743748c3188d485a4ba/wiki/campaigns/measurement_tools.md), [Mind claims at 35281b1d](https://github.com/PyAutoLabs/PyAutoMind/blob/35281b1d/active.md), [full dated review](../checkins/2026-10-13.md). Review date does not refresh measurement dates.
- Availability: project `hpc/sync jobs` returned an empty current queue; `hpc/sync status` timed out after 25 seconds during the output preview. Historical job outcomes, unpulled results and RAL cleanup contents are unverified; no collection or compute was performed.


## Evening check-in — 2026-10-13

Reviewed at 2026-10-13T17:51:40Z. Unstarted (no PR/issue/branch/results, 2026-10-04). Select one bounded step when prioritised.

[Full campaign/task review](../checkins/2026-10-13-evening.md) records verified
GitHub sources and limits. Current RAL queue was empty; the transfer preview timed
out, so historical jobs and unpulled results remain unverified. Review time does
not refresh measurements or authorize compute. Historical task text is retained.


## Check-in 2026-10-17 (evening)

- **Measured on the A100** under autolens_profiling issue #429, PR [#433](https://github.com/PyAutoLabs/autolens_profiling/pull/433) (OPEN, CI green, unmerged; titles still name the CPU route constants, which were dropped). RAL job 412515, `euclid-ral-gpu-1`, A100 80GB, JAX 0.10.2, fp64, private 2026.10.17.1 stack, compile excluded. Note `results/notes/interferometer_w_tilde_fft_size_levers_2026_10.md`; witness `results/breakdown/interferometer/jvla/delaunay_hpc_a100_fp64_fft_prune.json`. Heart read STALE ("release validation incomplete: no rehearsal for current source"); no override used.
- **(1) Pruned padded FFT vs library F** (Delaunay-1500, batch 128): alma 140² 17.97 → 14.49 ms, alma_high 280² 65.45 → 50.96 ms, jvla 700² 499.6 → 351.2 ms (F saving 19.4 / 22.1 / 29.7 %; whole likelihood 1.08× / 1.18× / 1.41×). F max rel diff ≤ 1.7e-15 (bar 1e-12), figure-of-merit shift 0 (bar 1e-6 nats). The saving grows with extent; four 1-D cuFFT calls beat one 2-D call at every extent measured.
- **(2) Real-space pixel scale at jvla:** 0.015 / 0.02 / 0.025″ instead of 0.01″ cuts F 1.53× / 4.09× / 7.61× but shifts log evidence +1,310 / +1,807 / +2,757 nats (mesh rebuilt per scale), failing the 0.5-nat bar: a modelling choice, not a speed setting. No workspace docs prompt. At 0.015″ the padded length 932 = 2²·233 limits the gain (awkward FFT lengths matter on the GPU too).
- **Human decision 2026-10-17 (chat):** interferometer GPU levers — "file wiki research but not make source code changes for now". The PyAutoArray `apply_operator` JAX pruning prompt is NOT filed; the prototype (`apply_pruned` / `curvature_pruned` in `scripts/interferometer/delaunay/fft_size_levers.py`) stays in the project. Route-constant refit on CPU deferred (CPU lane closed). Status → parked (research filed).
- [Full dated review](../checkins/2026-10-17.md). Review time does not refresh measurements or authorize compute; merge is the human's.

---

# Interferometer W~ curvature matrix is FFT-bound on the mask extent: pruned padded FFT and real-space pixel scale on the A100

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
- PyAutoArray
Themes:
- interferometer
- pixelization
- likelihood-profiling
- jax-gpu
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Consequence: glance
Witness: `results/breakdown/interferometer/jvla/delaunay_hpc_a100_fp64_fft_prune.json` has a pruned-vs-library F row at alma, alma_high and jvla. The pruned F agrees with the library F to max rel diff ≤ 1e-12 and the figure of merit to ≤ 1e-6 nats. The file also has an F-vs-real-space-pixel-scale row at jvla (0.01 / 0.015 / 0.02 / 0.025″) with the log-evidence shift against the 0.01″ reference.
Review-minutes: 10
Unattended: ready
Lane: local-dev
Epic: interferometer-likelihood-campaign
Filed: 2026-09-27

Follow-up to autolens_profiling#320, lever 2
(`results/notes/interferometer_mesh_a100_breakdown_2026_09.md`, "Ranked levers" §2).

## Why

On the A100 the W~ curvature matrix F = Aᵀ W~ A is 36–42 % of the sparse-path pixelized
likelihood at alma, 66–73 % at alma_high and 91–92 % at jvla (510 of 563 ms, Delaunay-1500).
Its cost is set by the mask extent M = y·x (70² / 140² / 280² / 700² at sma → jvla), not by
N_vis.

- The block-size sweep is flat (alma B = 32–512: 17.8–19.3 ms).
- The kernel split puts the FFT apply at 71–85 % of F.
- So F is **FFT-bound** on the (B, 2y, 2x) `rfft2` / `irfft2` pair.

The extent is already the mask bounding box (PyAutoArray `mask/mask_2d.py:746-776`
`extent_index_for_masked_pixel`), and the (2y, 2x) pad is the minimum for a linear
correlation. Only two things are left to change: how much of the padded transform is computed,
and how big the extent is.

## What

1. **Pruned padded transform (measurement first, harness-only).**
   `InterferometerSparseOperator.apply_operator` (PyAutoArray
   `inversion/inversion/interferometer/inversion_interferometer_util.py:1099-1151`) pads each
   (B, y, x) block to (B, 2y, 2x) and runs full 2-D `jnp.fft.rfft2` / `irfft2` (`:1145-1150`).
   Only the top-left y × x quadrant of the input is non-zero, and only the top-left y × x of the
   output is kept (`:1150`).
   - Write a harness copy of `curvature_matrix_diag_from` (`:1171-1253`) whose apply is
     separable: `rfft` along x on the y non-zero rows (x padded to 2x), zero-pad y, `fft` along
     y, multiply by `Khat`, `ifft` along y and keep y rows, `irfft` along x with `n = 2x`,
     keep x.
   - That removes up to ~25 % of the FFT work. The bound is ≤ ~15–20 % of F (~90 ms at jvla,
     ~3 ms at alma).
   - Measure it against the library F inside the same fused jit at alma / alma_high / jvla,
     Delaunay and rect. One cuFFT 2-D call may beat four 1-D calls, so record a no-go honestly.
2. **Real-space pixel scale at jvla (measurement, science-gated).** jvla at 0.01″ is a 700²
   extent. Re-run the jvla Delaunay-1500 cell at real-space pixel scales 0.015 / 0.02 / 0.025″
   (mask radius fixed at 3.5″; `instruments/interferometer.py` jvla entry). Record F, the full
   call and the log-evidence / reconstruction shift against 0.01″. Predicted: 2× coarser gives
   ~4× smaller M, putting F near the alma_high row (~67 ms). Whether the science tolerates it is
   the question, not the speed. The mask-radius half (2.0 / 3.5 / 5.0″) is in task 3/3's
   decision matrix on CPU (`complete/archive/epics/interferometer_likelihood_campaign.md`, retired 2026-09-30; the matrix is `results/notes/interferometer_likelihood_decision_matrix_2026_09.md`);
   do not duplicate it.
3. Verdict in a note section. If (1) wins by ≥ 10 % of F at jvla with a ≤ 1e-12 F match, file
   the PyAutoArray change (the NumPy branch `:1155-1169` gets the same pruning via
   `scipy.fft`). If (2) holds the 0.5-nat bar at a coarser scale, file a workspace docs prompt
   for interferometer real-space grid guidance.

## Not in scope

The fp32 FFT arm (slower on the A100 and fails the bar at jvla, #320), block size (flat), and
mixed precision (does not reach F).
