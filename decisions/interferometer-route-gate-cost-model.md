# Route interferometer curvature by a calibrated two-constant cost model

Date: 2026-10-15
Decision maker: James Nightingale
Decision source: The plan on [PyAutoArray#628](https://github.com/PyAutoLabs/PyAutoArray/issues/628) was approved under `--auto` in session 3e3dea38. On 2026-10-15 the human merged [PyAutoArray#632](https://github.com/PyAutoLabs/PyAutoArray/pull/632) by `/prm`, answering "merged-unchanged" (Mind `complete/2026/10/interferometer-numba-route-gate.md`). The decision is recorded on the human's explicit direction in the same session ("Yes, record it as my decision").

## Campaign

This decision belongs to the interferometer campaign, task `interferometer_large_mask_aris`
([PyAutoPulse#62](https://github.com/PyAutoLabs/PyAutoPulse/issues/62)).

A NumPy single-mapper interferometer inversion builds its curvature matrix by one of two routes: the
numba `direct_conv` kernel or the FFT route. A fixed gate of 60 mean non-zeros per source column
chose between them. It was calibrated on the autolens_profiling#226 geometries.

On the Aris 512×512 mask (91,507 px, extent 341², padded FFT grid 682²), the gate sent 2,577 vertices
(106 nnz/col) to FFT at 44.1 s/call, although `direct_conv` measured 34.2 s. The question was whether
to retune a constant or replace it.

## Evidence

The fit and checks are at PyAutoArray `17caf228` (the merge of #632). The timings are single-thread
laptop medians (i9-10885H, WSL2) on PyAutoArray `ccddfba6`, measured before the change. The machine
was shared, and the bake-off notes about 2.5× clock drift between sessions, so the ratios matter,
not the absolute seconds.

- **512×512 table** (s/call; FFT / direct_conv). The old gate mis-routes 2,577 vertices.

  | Vertices | nnz/col | FFT | direct_conv |
  |---|---|---|---|
  | 1,459 | 187.6 | 28.3 | 38.4 |
  | 2,577 | 106.2 | 44.1 | 34.2 |
  | 5,746 | 47.7 | 97.3 | 41.2 |

  The measured crossover on this mask lies between 106 and 188 nnz/col, against about 60
  (Delaunay) and 77 (rectangular) at the #226 extents.
- **Model.**
  - `t_fft = c_fft · S · W_fft(2ny × 2nx)`, where `W_fft` is pocketfft's `cost_guess` for
    rfft2 + irfft2 of the padded extent.
  - `t_dc = c_dc · nnz · ny · nx`.
  - `c_fft` = 7.62e-10 and `c_dc` = 1.77e-09, from a least-squares fit on log seconds over 9 paired
    timings: the 6 #226 bake-off cells and the 3 Aris 512 points.
  - The model picks the faster route at 9/9. Measured/predicted ratio residuals are 0.68–1.47
    (log-rms 0.26).
  - A micro-benchmark at padded lengths 140–682 varied 1.8× in seconds per model unit, against 5.8×
    in seconds per `N log2 N`.
- **Phase 2, on Aris with default settings.**
  - Source: [autolens_profiling#420](https://github.com/PyAutoLabs/autolens_profiling/pull/420), head
    `32372865`, **at PR-open, not merged**.
  - The factory picks the faster measured arm in 6/6 cells: 125×125 (extent 83²) at
    1,405/2,947/5,526 vertices goes to `direct_conv`; 512×512 at 1,459 goes to FFT and at
    2,577/5,746 to `direct_conv`.
  - **Limit 1:** the three 512 pairs are calibration points, so agreement there is in-sample.
  - **Limit 2:** the 125 NumPy FFT arm was never timed. The comparison there uses the JAX-jit FFT
    route (2.8–3.6 cores) as a proxy.
  - The record also notes that a constant of about 150 would route those six cells correctly. The
    case against a constant rests on the model's extent dependence: the modelled crossover is about
    309 nnz/col at 83² and about 166 at 341².
- **Tests (#632).** PyAutoArray 2055 passed, 4 xfailed; PyAutoGalaxy 1357; PyAutoLens 832, 1 xfailed.
  A 12-point routing test covers Aris 512 ×3, Aris 125 ×3 and the bake-off ×6. Smoke ran 165/165,
  and the independent re-review was CLEAN.

## Options considered

- **Keep the fixed gate of 60.** It mis-routes the Aris 512 mask at 2,577 vertices (1.29× slower).
- **A per-mask-size table of gates.** It does not generalise to an unmeasured extent and needs
  re-measuring for each mask.
- **An `N log2 N` FFT work form.** No single constant ratio routes both data sets. Fitted on all nine
  points it mis-routes Aris 512 at 2,577, the bug being fixed. Fitted on the 512 points alone it
  mis-routes two bake-off cells. The awkward Aris FFT lengths explain the gap: 682 = 2·11·31, and
  166 = 2·83 is pocketfft's Bluestein case.
- **The pocketfft factorisation-aware form** (chosen). Two constants, with work priced by the FFT
  library's own planner estimate.

## Decision

- The default curvature routing for NumPy single-mapper interferometer inversions is the calibrated
  two-constant cost model. The packaged `interferometer_numba_nnz_per_source_max` is now `null`.
- An explicit positive `interferometer_numba_nnz_per_source_max` stays a hard gate, with its old
  meaning.
- `0` stays the kill switch for numba.
- The new `interferometer_route: "numba" | "fft"` forces a route.

## Implications

- **Shipped in [#632](https://github.com/PyAutoLabs/PyAutoArray/pull/632)** (merge `17caf228`,
  pending release), together with the helpers `curvature_route_seconds_from`, `fft_route_work_from`
  and `direct_conv_work_from`. The likelihood is unchanged, because both routes are pinned equal by
  parity tests. Only speed changes.
- **A fit may now take a different route than before:** numba at higher nnz/col on large extents, or
  FFT at lower nnz/col on small extents with smooth FFT lengths.
- Scripts that set the gate explicitly keep their meaning. To revert, set the gate back to `60.0`
  in config or `Settings`.
- **Follow-up (low).** The autolens_profiling decision-matrix note may still describe gate 60 as
  current. This was a review finding on #420.

## Revisit conditions

- **The direct_conv kernel changes.** The symmetric row-restriction lever (Mind draft
  `direct_conv_symmetric_row_restriction`, estimated 2–2.5× at 512 but unconfirmed) changes kernel
  work per extent, so the constants must be refitted. `direct_conv` may then win at 1,459 vertices
  on 512×512 too.
- **Masks outside the calibrated range.** Calibration extents span 70²–341². No point near the
  modelled 83² crossover (~309 nnz/col) has been measured. A new mask extent should get one paired
  measurement before its routing is trusted.
- **Out-of-sample evidence.** A paired timing that contradicts the chosen route, the NumPy FFT arm
  timed on the 125 mask, or a change of FFT backend, BLAS or CPU class that alters the
  FFT/`direct_conv` cost ratio.

## History

This is the first decision on this question. It supersedes nothing.
