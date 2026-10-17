# DelaunayNN (Sibson) imaging likelihood at close to Delaunay cost on the numba/NumPy CPU path

- Campaign: `delaunay-nn-cpu` (parked, human decision 2026-10-17, chat: "file in research to come back to in the future")
- Issue: [PyAutoArray#629](https://github.com/PyAutoLabs/PyAutoArray/issues/629)
- PR: [PyAutoArray#637](https://github.com/PyAutoLabs/PyAutoArray/pull/637) (OPEN, CI 3 legs green, pending-release, unmerged; merge is the human's)
- Prior work: [PyAutoArray#624](https://github.com/PyAutoLabs/PyAutoArray/pull/624)/[#625](https://github.com/PyAutoLabs/PyAutoArray/pull/625) (issue #623, numba Sibson kernel; released 2026.10.16.1): Aris SMA 1,405 vertices DelaunayNN 18.1 s → 0.57 s (Delaunay 0.41 s), threads=1, logL identical.

## Question

Can natural-neighbour (Sibson) interpolation run in the CPU imaging likelihood at close to Delaunay
cost? The draft target was ~1.5× Delaunay at sub-size 4.

## Measurement (PyAutoArray#637)

RAL `euclid-ral-compute-10-4`, `--partition=ral --exclusive`, 1 thread, `use_jax=False`; A-B-B-A × 2
blocks, 10 timed calls per process after 2 warm-ups. A = PyAutoArray `e59d5fa9` (2026.10.17.1),
B = the #637 head; other libraries 2026.10.17.1. HST imaging, 1,030 vertices, 15,380 pixels.
Heart read STALE ("release validation incomplete: no rehearsal for current source"); no override used.

| Case | A | B | Ratio to Delaunay (B) | adaptive_pixel_signals A → B | unique_mappings A → B |
|---|---|---|---|---|---|
| DelaunayNN sub 4 | 0.569 s | 0.392 s | 2.20× (was 3.00×) | 158.0 → 6.5 ms | 22.5 → 17.0 ms |
| Delaunay sub 4 | 0.189 s | 0.178 s | 1 | 10.0 → 1.2 ms | 4.4 → 3.5 ms |
| DelaunayNN sub 2 | 0.235 s | 0.189 s | 1.75× (was 2.10×) | 37.3 → 1.1 ms | 4.3 → 2.7 ms |
| Delaunay sub 2 | 0.112 s | 0.108 s | 1 | 2.5 → 0.4 ms | 1.9 → 1.1 ms |

- logL bit-identical in all four cases.
- Sibson interpolation itself is ~0.16 s at sub 4 (~41 % of the DelaunayNN call).
- **Target ~1.5× not met** (2.20× at sub 4). The remaining cost is Sibson work and wider curvature
  rows (up to 43 unique pixels per data pixel against 27 for Delaunay), not padding overhead.
- #637 also fixes the size-0 Sibson NaN edge case: failed rows now keep `size >= 1` with a NaN weight
  on the nearest seed vertex (reference, numba and JAX paths), so a failed row no longer yields a
  finite, wrong evidence.

## Knowledge

- **Padded rows.** DelaunayNN tables are 32 columns wide (`SIBSON_MAX_NEIGHBORS`), but HST-scale
  imaging uses at most 13 slots per row (mean 7.2). `adaptive_pixel_signals_from` used `np.add.at`
  over all 32 slots of 246k sub-pixels; visiting only live entries cuts it from 158 to 6.5 ms with an
  unchanged summation order.
- **Misattribution trap.** cProfile charged ~0.30 s to `mapper.unique_mappings`; most of it was the
  Sibson interpolation running lazily on first access to the mapper's tables. Time kernels directly
  before acting on cumulative profiles of cached properties.
- **Imaging vs interferometer.** On the Aris interferometer the visibility-side curvature dwarfs the
  mapping tables, so DelaunayNN sits near ~1.4× Delaunay. Imaging at sub 4 has 16× as many query
  points and cheap curvature, so per-sub-pixel table work and Sibson set the ratio.

## Future work (recorded, not filed)

Per the human decision of 2026-10-17 these stay as research:

- The ~1.5× target: Sibson kernel cost at threads=1 and curvature over wider unique rows.
- Hazard: `sub_slim_indexes_for_pix_index` padding.
- Hazard: Sibson rows with mid-row gaps.

## Check-in 2026-10-17 (evening)

- Campaign created parked (human decision 2026-10-17, chat). #637 recorded at PR-open; it is file-
  disjoint from PyAutoArray#636 and independent of it.
- [Full dated review](../checkins/2026-10-17.md).

### Post-/prm 2026-10-17

- **Merged 2026-10-17 (human /prm):** [PyAutoArray#637](https://github.com/PyAutoLabs/PyAutoArray/pull/637) (pending-release).
- **Issues closed:** PyAutoArray#629.
- **Mind record:** [`delaunaynn-wide-row-overhead`](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/10/delaunaynn-wide-row-overhead.md).
