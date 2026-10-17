# Gate the symmetric direct_conv kernel at work fraction 0.7, with ymin column ordering

Date: 2026-10-16
Decision maker: James Nightingale
Decision source: The human paused session 13efb443 on 2026-10-16 with the decision "rank columns by ascending ymin and raise the default gate from 0.5 to 0.7", recorded in the checkpoint comment on [PyAutoArray#635](https://github.com/PyAutoLabs/PyAutoArray/issues/635) ("Human decision (2026-10-16)").

## Campaign

This decision belongs to the interferometer campaign, task `interferometer_large_mask_aris`
([PyAutoPulse#62](https://github.com/PyAutoLabs/PyAutoPulse/issues/62)), lever L2.

The numba `direct_conv` curvature kernel convolves every source column over the whole extent
rectangle. A symmetric, row-restricted variant computes only one triangle of F, restricted to the
extent rows later-ranked columns span and each row's mask x-range, then mirrors it. Its computed
entries are bit-identical.

Two questions remained: when the variant should run, and how the columns should be ordered. The
ordering decides how much work it skips.

## Evidence

All timings are serial numba, compile excluded. Library: PyAutoArray `e59d5fa9` plus the #635 patch
(PR [#636](https://github.com/PyAutoLabs/PyAutoArray/pull/636), head `62a1e3ac`). Record:
autolens_profiling [#425](https://github.com/PyAutoLabs/autolens_profiling/pull/425),
`results/notes/interferometer_direct_conv_symmetric_2026_10.md`.

- **Cost model.** The symmetric kernel takes κf of the full kernel's time, with κ = 1.32. κ was
  fitted on synthetic Aris-512 geometry on RAL (job 411835, `euclid-ral-compute-1`, load < 1;
  measured/predicted 0.99–1.01).
- **Real Aris data, before the decision** (laptop, shared, 1,459 vertices):
  - With centroid ordering, f = 0.587, measured 1.32× (predicted 1.29×).
  - With `ymin` ordering, f = 0.511, measured 1.46× (predicted 1.48×).
  - The original 0.5 gate kept Aris on the full kernel either way.
  - Real columns are tall because of multiple imaging: the median spans 90 of 341 rows, against 15
    synthetic.
- **After the decision, on RAL** (`euclid-ral-compute-1`, `ral`, exclusive, load ≤ 1, jobs
  412490–412493), `ymin` order, default gate 0.7:
  - Real Aris: 1.49× / 1.53× / 1.58× at 1,459 / 2,577 / 5,746 vertices. log L matches to round-off;
    a log-det triangle control shows the 5,746-vertex 0.0071-nat difference is round-off.
  - Synthetic: 1.83× / 1.86× / 1.90×.
- **Uncertainty.** κ has been measured only at f 0.40–0.51, so the predicted 1.08× at f = 0.7 is
  an extrapolation. There is one real dataset. At 1,459 vertices the FFT route measures 15.32 s on
  the same node, so the gain over the previous default route there is about 1.02×.

## Options considered

- **Keep the gate at 0.5 with centroid ordering.** This is safe but excludes real multiply imaged
  data (f ≈ 0.51–0.59), so it gives no gain where the campaign needs one.
- **Gate at 0.5 with `ymin` ordering.** Real Aris sits at f ≈ 0.50–0.51, right on the boundary, so
  it would flip between kernels across meshes.
- **Gate at 0.7 with `ymin` ordering (chosen).** It sits below the model's break-even of f = 0.76,
  keeps a predicted gain of at least 1.08×, and covers multiply imaged data with margin.
- **No gate (always symmetric).** Above f ≈ 0.76 the model predicts a slowdown.

## Decision

- Rank source columns by ascending `ymin` (stable, empty columns last).
- Set the packaged default of `interferometer_direct_conv_symmetric_max_work_fraction` to **0.7**.
  `0` disables the kernel, and `null` means the default.
- The scope is the serial numba `direct_conv` route only. The parallel kernel and the JAX routes
  are unchanged.

## Implications

- With serial numba, NumPy interferometer fits with f ≤ 0.7 use the symmetric kernel by default
  once PyAutoArray#636 is merged and released. Results are identical to round-off, so this is a
  speed change only.
- The #632 route model now scales `t_dc` by `min(1, κf)`. On the Aris 512 mask at 1,459 vertices
  this flips the route from FFT to `direct_conv`. That is correct on RAL, but only by about 1.02×.
- **Shipped:** PR-open, pending release (PyAutoArray#636; record autolens_profiling#425). Merge is
  the human's.
- **Follow-up (deferred):** on RAL, FFT/full `direct_conv` measures 0.68 against 0.89 predicted by the
  laptop-calibrated #632 constants. A cluster-node refit is deferred: the human closed the
  interferometer CPU lane on 2026-10-17 (chat).

## Revisit conditions

- A dataset where the kernel runs at f between 0.6 and 0.7 and measures slower than the full
  kernel. That would mean κ is not constant up to the gate.
- A refit of the route constants that changes which route is chosen near the gate.
- A parallel symmetric kernel, which would need its own gate.

## History

This is the first record for this gate.
