# Exclude zero-weight mappings from AdaptSplit pixel signals on Delaunay meshes only

Date: 2026-10-15
Decision maker: the PyAutoLabs maintainer
Decision source: AskUserQuestion answer "Delaunay only (Recommended by review)" in session 3e3dea38, 2026-10-15. Quoted on [PyAutoArray#627 (issuecomment-6200058449)](https://github.com/PyAutoLabs/PyAutoArray/issues/627#issuecomment-6200058449). Recorded on the human's explicit direction in the same session ("Yes, record it as my decision").

## Campaign

This decision belongs to the interferometer campaign, task `interferometer_large_mask_aris`
([PyAutoPulse#62](https://github.com/PyAutoLabs/PyAutoPulse/issues/62)). The task profiles the Aris
SPT2319-55 interferometer setup: a Delaunay mesh with `AdaptSplit` regularization, on real-space
masks of 125×125 (5,496 px) and 512×512 (91,507 px), with 5.5M visibilities.

The numba/NumPy and JAX backends returned different log evidences at identical parameters. The whole
difference was in `log_det_regularization_matrix_term`: 2443.22 on numba against 2561.98 on JAX for
one 125×125 vector. Evidences were therefore not comparable across backends or across pipeline phases
that mix them. The issue was
[PyAutoArray#627](https://github.com/PyAutoLabs/PyAutoArray/issues/627).

## Evidence

The evidence is at PyAutoArray `ccddfba6` (before the fix) and `0377eeaa` (the merge of
[#631](https://github.com/PyAutoLabs/PyAutoArray/pull/631)), on the laptop in fp64. It is drawn from
the #627 comments "Root cause found" (issuecomment-6197915508) and "Parked at the review leg"
(issuecomment-6199913182), and from Mind `complete/2026/10/adaptsplit-logdet-backend-parity.md`.

- **The factorizations were not the cause.**
  - On each backend's own H, five methods agree with a 50-digit mpmath reference to ≤ 2e-8: NumPy
    dense Cholesky, SuperLU, JAX Cholesky, slogdet and diagonal scaling.
  - The two backends built different H matrices: max |H_np − H_jax| = 3.21, on max |H| 31.9.
- **Root cause.**
  - `adaptive_pixel_signals_from` divided each pixel's summed signal by a count that included
    zero-weight mapping entries.
  - The 125×125 mesh is a stride-2 subsample of the data grid, so 1,375 data points sit exactly on
    vertices. For such a point any surrounding triangle is valid.
  - scipy `find_simplex` and the JAX Delaunay walk chose different triangles in 1,114 of 5,496 rows.
    Both choices are geometrically correct.
  - The phantom zero-weight neighbours changed the counts, then the pixel signals (max diff 0.23),
    the AdaptSplit weights (0.53) and H.
  - Chi², the curvature matrix, the data vector and the curvature log det were unaffected.
- **Simulated fix: count only non-zero weights.** Signals agree to 4e-15 and H to 4.8e-13. The log
  det is 2468.446318 on both backends (Δ 4e-8).
- **Review finding on the first patch, which applied the rule to every interpolator.**
  - `KNNBarycentric` clips negative barycentric weights to exactly 0 for every query outside its
    3-nearest triangle, so whole regions are affected, not only coincident points.
  - Excluding those zeros would change its pixel signals and evidence broadly.
  - It would also add a jump in the likelihood: moving one weight from 1e-9 to 0 moved a test scalar
    from 6.2358 to 6.4889, and the gradient at w = 0 is exactly 0.
  - Rectangular bilinear meshes are affected only in exact-coincidence cases.
- **Shipped result (#631, Delaunay-only scope).**
  - On a synthetic ill-conditioned AdaptSplit case (cond ≈ 2.2e9), H parity is 3.6e-15 and the
    log dets are 2.1e-9 apart, both within 1.7e-9 of a 50-digit reference.
  - The independent re-review found KNN, KNNBarycentric and rectangular bit-identical to main.
- **After-measurement on the Aris data.**
  - Source: [autolens_profiling#420](https://github.com/PyAutoLabs/autolens_profiling/pull/420), head
    `32372865`, **at PR-open, not merged**, on PyAutoArray `17caf228`.
  - numba and JAX agree to ≤ 4.4e-8 at all six cells (125: 1,405/2,947/5,526 vertices; 512:
    1,459/2,577/5,746).
  - The original 125×125 vector gives 2468.4463180 on both backends.
- **Limitation: a residual remains.** The split regularization builders add an absolute 1e-8 diagonal
  jitter. Once max(coeff)^4 ≳ 1e6, the log det is round-off-dominated (cond 1e16–1e17).
  - In 20 prior draws on 125×125 with the counting fix, 6 still differed by 5e-3–2.2.
  - This decision does not address the residual, and no work on it is filed.

## Options considered

- **(a) Accept the rule for every mesh, including KNN and KNNBarycentric.** This is the simplest
  code. But KNNBarycentric evidence would change across whole regions, and its likelihood would gain
  a discontinuity on a mesh used for gradient-based fits.
- **(b) Delaunay only** (chosen; recommended by the independent review). Exclude zero-weight mappings
  for Delaunay and DelaunayNN, and keep the old counting elsewhere. It fixes the parity bug where it
  arises, at the cost of one keyword and one interpolator class attribute.
- **(c) Weight-normalised signals.** Divide the summed signal by the summed weights rather than by a
  count, so zero weights drop out on every mesh without a jump. This was raised in the session as
  the route if KNN-family parity is ever needed. It was not prototyped or measured.
  - The #627 park comment listed a different third option: make the scipy/JAX triangle choice
    deterministic for coincident points and keep the count semantics. That option had been rejected
    earlier in the investigation.

## Decision

Exclude zero-weight mapping entries from the adaptive pixel-signal counts for Delaunay and
DelaunayNN interpolators only. KNN, KNNBarycentric and rectangular meshes keep the previous counting.

## Implications

- **Shipped in [#631](https://github.com/PyAutoLabs/PyAutoArray/pull/631)** (merge `0377eeaa`,
  pending release).
  - `adaptive_pixel_signals_from(..., exclude_zero_weight_mappings=False)` gains a keyword.
  - It is driven by the interpolator class attribute `exclude_zero_weight_mappings`: True on
    InterpolatorDelaunay and InterpolatorDelaunayNN, False on the base interpolator and KNN.
- **Evidence values change, the same way on both backends,** on Delaunay and DelaunayNN meshes where
  data points sit exactly on vertices or edges, for example Overlay or grid-subsample image meshes.
  Any pinned evidence for such a mesh will shift. No smoke script failed (151/151), and no workspace
  change was needed.
- **KNN, KNNBarycentric and rectangular meshes are bit-identical** to the previous release.
- numba/JAX evidences on Delaunay AdaptSplit fits are now comparable to ~1e-8 at moderate
  coefficients. The high-coefficient jitter regime is still backend-sensitive.

## Revisit conditions

- **KNN-family parity is needed,** for example a KNNBarycentric backend-parity requirement. Then
  evaluate weight-normalised signals (option c), which avoids the discontinuity of option (a).
- **The jitter residual matters in practice.** That is, fits reach max(coeff)^4 ≳ 1e6, or the 512×512
  non-PD rate (~1 in 4 draws before #631) is still seen. A relative jitter
  (`1e-8 * max(regularization_weights**2)`) is the candidate. It changes evidence values, so it needs
  its own decision.
- **A change to the Delaunay point-location routines,** in scipy or the JAX walk, or a new
  interpolator whose weights can be exactly zero.

## History

This is the first decision on this question. It supersedes nothing.
