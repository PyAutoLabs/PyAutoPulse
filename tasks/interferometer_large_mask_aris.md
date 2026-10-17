# Interferometer large-mask likelihood — memory and routing (Aris 512×512)

Campaign: interferometer
Task: interferometer_large_mask_aris
Reviewed: 2026-10-15
Status: active (all three library members merged 2026-10-15, pending release; phase-2 record at PR-open as autolens_profiling#420; knowledge section written 2026-10-15; L1 Cholesky reuse in development)

Filed 2026-10-15 from the Aris interferometer profiling session (Delaunay + `AdaptSplit`,
`use_jax=False` numba route and JAX jit, real-space masks 125×125 at 5,496 masked pixels and
512×512 at 91,507 masked pixels, 5.5M visibilities, 682×682 W~ extent). The human asked for the
three resulting PyAutoArray tasks to be logged and monitored as one Pulse speed-up campaign.
Mind owns the repository claims and PR lifecycle (issues below); this task records the
campaign intent, the baseline numbers the tasks must beat, and each check-in.

## Members (Mind lifecycle, PyAutoArray; one claim at a time, in this order)

| # | Issue | Pass condition (Witness) | Mind state 2026-10-15 |
|---|-------|--------------------------|-----------------------|
| 1 | [PyAutoArray#626](https://github.com/PyAutoLabs/PyAutoArray/issues/626) sparse data vector | 512×512, 5,746 vertices, numba route: peak RSS 7.2 GB → ≤ ~3.5 GB, logL unchanged to 1e-8 | active, `--auto`, Heart RED development override |
| 2 | [PyAutoArray#627](https://github.com/PyAutoLabs/PyAutoArray/issues/627) AdaptSplit log-det parity | numba vs JAX `log_det_regularization_matrix_term` agree < 1e-3 (now 2443.22 vs 2561.98), regression test | queued behind #626 (planned.md) |
| 3 | [PyAutoArray#628](https://github.com/PyAutoLabs/PyAutoArray/issues/628) numba route gate cost model | both masks pick the faster of direct_conv vs FFT at every tested vertex count | queued behind #627; DelaunayNN #624/#625 merged so no factory conflict |

## Baseline measurements (s/call, 1 thread, laptop; PROGRESS4 steps 8.3–8.4)

512×512 mask, 91,507 masked pixels, regular-step Delaunay meshes:

| vertices (nnz/col) | NumPy FFT route | numba direct_conv | JAX jit (cores) | peak RSS |
|---|---|---|---|---|
| 1,459 (188) | 28.3 | 38.4 | 18.3 (1.59) | 4.13 GB FFT / 3.22 DC / 3.69 JAX |
| 2,577 (106) | 44.1 | 34.2 | 32.2 (1.75) | 4.34 / 3.41 / 5.02 |
| 5,746 (48) | 97.3 | 41.2 | not run (8.95 GB XLA compile temp) | 7.14 / 7.17 / — |

- Default gate 60 nnz/col mis-routes 2,577 vertices to FFT (1.29× slower); measured crossover ~140–150 nnz/col on this mask vs ~60 (Delaunay) / ~77 (rectangular) on 125×125 (autolens_profiling#226).
- Memory culprit: `sparse.py:104` `data_vector = mapping_matrix.T @ dirty_image` materialises the dense (91,507 × S) matrix: 1.07 / 1.9 / 4.2 GB at 1,459 / 2,577 / 5,746 vertices, route-independent.
- Backend parity: chi², curvature, data vector, curvature log-det identical to 1e-16 relative; only the AdaptSplit regularization log-det differs (125×125: 2443.22 numba vs 2561.98 JAX; 512×512 @1,459: 2576.59 vs 2574.73). ~1 in 4 draws non-PD (numba LinAlgError vs JAX -inf).

These are laptop timings under load and qualify no baseline; the campaign's after-measurements
re-run the same cached setups and are recorded here per task. Caches live in a session
scratchpad (temporary); the numbers above are the durable record.

## Check-in 2026-10-15

- Filed: #626 active (worktree `interferometer-sparse-data-vector`), #627 and #628 queued in Mind planned.md. Implementation worker running on #626; read-only root-cause investigation running for #627.
- Next: after #626 PR-open and human `/prm`, start #627 (`/start_library`), then #628. Record each task's before/after witness table here on close-out.

## Results 2026-10-15

All three members merged on 2026-10-15 and are pending release. The tables below are copied
from the PR bodies and the Mind completion records. Timings are not claimed: the machine's
load average was 2–14 during measurement.

### 1. Sparse data vector — [PyAutoArray#630](https://github.com/PyAutoLabs/PyAutoArray/pull/630) (merged 7cc71238)

| run (Aris 512×512) | before | after |
|---|---|---|
| numba, 5,746 vertices, peak RSS | 7.17 GB | **3.14 GB** |
| JAX jit, 1,459 vertices, peak RSS | 3.65 GB | 2.60 GB |
| JAX, 5,746 vertices, XLA compile temp | 8.95 GB | 1.86 GB |
| JAX jit, 5,746 vertices | infeasible | runs, peak RSS 3.24 GB |

- The data vector matches the dense `mapping_matrix.T @ d~` to 5.8e-16 relative. The log likelihood moves by at most 2.5e-11 relative (≈3.5e-4 nats at |logL| ≈ 1.4e7).
- Decision taken: the witness "logL unchanged to 1e-8" was read as fp64 precision, because an absolute 1e-8 is below float64 resolution at this logL. Revert: `git revert 8676b6a0`.

### 2. AdaptSplit log-det backend parity — [PyAutoArray#631](https://github.com/PyAutoLabs/PyAutoArray/pull/631) (merged 0377eeaa)

| check | before | after |
|---|---|---|
| synthetic ill-conditioned AdaptSplit Delaunay H (cond ≈ 2.2e9), NumPy vs JAX | different H | H parity 3.6e-15 |
| same, log-det NumPy vs JAX | — | Δ 2.1e-9; both within 1.7e-9 of a 50-digit mpmath reference |
| Aris 125×125 dump, log-det (investigation's simulated fix) | 2443.22 numba vs 2561.98 JAX | 2468.446318 on both |

- Root cause: the log-det code was correct. `adaptive_pixel_signals_from` counted zero-weight mappings for data points lying on a vertex or edge, and scipy and the JAX Delaunay walk pick different triangles for those points. The two backends therefore built different H matrices.
- Fix: zero-weight mappings are excluded for Delaunay and DelaunayNN only. The human chose this scope after review, because KNNBarycentric clips weights to zero over whole regions. KNN, KNNBarycentric and rectangular meshes are bit-identical.
- Owed: the Aris setup was not re-run on the branch. The after-measurement goes into the phase-2 record (in flight as a separate autolens_profiling task).

### 3. Numba route-gate cost model — [PyAutoArray#632](https://github.com/PyAutoLabs/PyAutoArray/pull/632) (merged 17caf228)

| mask (extent) | vertices | nnz/col | measured faster | chosen (cost model) | old gate 60 |
|---|---|---|---|---|---|
| 512×512 (341²) | 1,459 | 187.6 | FFT | FFT ✓ | FFT |
| 512×512 (341²) | 2,577 | 106.2 | numba | numba ✓ | FFT ✗ |
| 512×512 (341²) | 5,746 | 47.7 | numba | numba ✓ | numba |
| 125×125 (83²) | 1,405 / 2,947 / 5,526 | 11.7 / 5.6 / 3.0 | numba | numba ✓ | numba |

- Cost model: `t_fft = c_fft · S · FFT work` (pocketfft `cost_guess` over the padded extent) and `t_dc = c_dc · nnz · ny · nx`, with c_fft 7.62e-10 and c_dc 1.77e-09. It was fitted on 9 paired timings and picks the faster route at 9/9, with residual ratios 0.68–1.47. Mask extents are 341² and 83²; 682 was the padded FFT grid.
- Settings: `interferometer_numba_nnz_per_source_max` null means the cost model (new default), a positive value is a hard gate, and 0 turns numba off. The new `interferometer_route` setting forces `"numba"` or `"fft"`. Revert: set the gate back to 60.
- The routing above is a live routing-only check. The timings come from the baseline table and were not re-run.

### Next

The autolens_profiling phase-2 record is at PR-open
([autolens_profiling#420](https://github.com/PyAutoLabs/autolens_profiling/pull/420), not merged). Its six-cell
table is copied under Knowledge (e) below. When #420 merges, re-pin that table to the merge commit. Then close the
task, or keep it open while L1 is in development. Later work is listed in Knowledge (f).

## Knowledge (2026-10-15)

This section is for whoever plans the next interferometer CPU campaign. It says where one likelihood
call spends its time and memory after the three fixes, what the routing model assumes, and which
levers are left, with their measured or estimated sizes.

**Timing caveat.** All timings come from one shared laptop (i9-10885H, WSL2, single-thread numba,
OpenBLAS 0.3.29). The load average was 2–14 during the evening. Read the timings as ratios and
fractions, not as absolute seconds, and re-time on a quiet core or a cluster node before using them
as a baseline. None of these numbers qualifies a baseline.

**Sources.**
- Library: PyAutoArray [#630](https://github.com/PyAutoLabs/PyAutoArray/pull/630) (merge `7cc71238`),
  [#631](https://github.com/PyAutoLabs/PyAutoArray/pull/631) (`0377eeaa`) and
  [#632](https://github.com/PyAutoLabs/PyAutoArray/pull/632) (`17caf228`). Issues
  [#626](https://github.com/PyAutoLabs/PyAutoArray/issues/626), [#627](https://github.com/PyAutoLabs/PyAutoArray/issues/627)
  and [#628](https://github.com/PyAutoLabs/PyAutoArray/issues/628).
- Mind completion records under `complete/2026/10/`: `interferometer-sparse-data-vector`,
  `adaptsplit-logdet-backend-parity` and `interferometer-numba-route-gate`.
- Phase-2 record: [autolens_profiling#420](https://github.com/PyAutoLabs/autolens_profiling/pull/420)
  (head `32372865`, PR-open).
- CPU speed-up research: PyAutoArray main `17caf228`, summarised in
  [PyAutoPulse#62 check-in](https://github.com/PyAutoLabs/PyAutoPulse/issues/62#issuecomment-6203354375).
  The full report sits in the session 3e3dea38 scratchpad, which is temporary, so this section is now
  its durable record.
- Lever prompts in PyAutoMind: `active/reuse_cholesky_factor_for_solve_and_log_det.md` (`fc12f450`,
  PyAutoArray [#633](https://github.com/PyAutoLabs/PyAutoArray/issues/633)) and
  `draft/feature/autoarray/direct_conv_symmetric_row_restriction.md` (`4d42e3d4`).

### (a) Where one likelihood call goes after the three fixes

The setup is Aris SPT2319-55 at PyAutoArray `17caf228`: Delaunay with `AdaptSplit`, an Isothermal +
ExternalShear lens with positions, `use_positive_only_solver=False`, the numba route, 1 thread, and
cProfile over 3 calls. On the 125×125 mask (5,496 px, extent 83², 5.5M visibilities):

| Piece | 1,405 vertices | 2,947 vertices (the source-plane mesh) |
|---|---|---|
| Full call | 0.63 s | 2.0–2.4 s |
| Curvature F (numba `curvature_direct_conv`) | 290 ms (53%) | 440 ms (18%) |
| `np.linalg.solve(F+H, D)` (LU) | 100 ms (18%) | 976 ms (40%) |
| `np.linalg.cholesky(F+H)` for the log det | 70 ms (13%) | 741 ms (31%) |
| Delaunay (qhull, find_simplex, split points) | 17–20 ms (3%) | 40–50 ms (2%) |
| H build + sparse log det H | 17–22 ms | 75 ms |
| Data vector (#630 sparse path) | 1 ms | 1 ms |

- Two dense factorizations of the same SPD matrix F+H take 31% of the call at 1,405 vertices and 72%
  at 2,947. Above about 2k vertices these factorizations, not the curvature, set the cost.
- On the 512×512 mask (91,507 px, extent 341²) the curvature build is 96–98% of the call on either
  route. Measured curvature-route times are 28–97 s per call; see (e).
- The old "fnnls + D 777 ms" line is obsolete. D takes 1 ms after #630, and
  `use_positive_only_solver=False` runs no fnnls.

### (b) Memory: the culprit and the fix (#630)

- **Culprit.** `data_vector = mapping_matrix.T @ dirty_image` built the dense (91,507 × S) mapping
  matrix: 1.07 / 1.9 / 4.2 GB at 1,459 / 2,577 / 5,746 vertices, on either route.
- **Fix.** #630 replaces it with a segment-sum over the sparse mapping triplets.
- **Effect at 512×512.**
  - numba at 5,746 vertices: peak RSS 7.17 → 3.14 GB.
  - JAX jit at 1,459 vertices: 3.65 → 2.60 GB.
  - JAX XLA compile temp at 5,746 vertices: 8.95 → 1.86 GB, so the JAX jit fit now runs at 3.24 GB
    peak; before, it was infeasible.
- **Accuracy.** The data vector matches the dense product to 5.8e-16 relative. The log likelihood
  moves by at most 2.5e-11 relative, about 3.5e-4 nats at |logL| ≈ 1.4e7.

### (c) The backend log-det difference: root cause and the residual

- **Cause.** The numba and JAX backends built different AdaptSplit H matrices. The log-det code was
  never the problem.
  - `adaptive_pixel_signals_from` counted zero-weight mapping entries.
  - For a data point lying exactly on a vertex or edge, scipy's `find_simplex` and the JAX Delaunay
    walk legitimately pick different triangles. That is 1,114 of 5,496 rows on the 125×125 stride-2
    mesh, where 1,375 points sit on vertices.
  - The zero-weight entries therefore landed on different pixels and changed the per-pixel counts.
    That changed the pixel signals (max diff 0.23), the AdaptSplit weights (0.53) and H (3.2 on
    max |H| 31.9).
  - Zero weights add nothing to the mapping matrix, which is why chi², the curvature matrix, the data
    vector and the curvature log det stayed identical.
- **The factorizations were accurate.** On each backend's own H, all five factorizations agree with a
  50-digit mpmath reference to ≤ 2e-8: dense Cholesky, SuperLU, JAX Cholesky, slogdet and diagonal
  scaling. The evidence is the "Root cause found" comment on
  [#627](https://github.com/PyAutoLabs/PyAutoArray/issues/627#issuecomment-6197915508).
- **Fix (#631).** Zero-weight mappings are excluded from the counts for Delaunay and DelaunayNN only.
  This was the human's decision; see
  [the decision record](../decisions/adaptsplit-zero-weight-delaunay-only.md).
  - On the Aris setup, numba and JAX now agree to ≤ 4.4e-8 at all six cells of (e).
  - At the original 125×125 vector, 2443.22 vs 2561.98 became 2468.4463180 on both backends.
- **Residual (unfiled).** The split regularization builders add an absolute 1e-8 diagonal jitter.
  Once max(coeff)^4 ≳ 1e6, the constant mode's eigenvalue is round-off-dominated (cond 1e16–1e17).
  The log det then differs between two near-identical H matrices, and round-off decides whether H is
  positive definite at all.
  - Over 20 prior draws on 125×125 with the counting fix: 12/20 agree to ≤ 1e-6, 2 more to < 1e-3,
    and the remaining 6 differ by 5e-3–2.2 (their max(coeff)^4 is 5e6–3.4e9).
  - No factorization or scaling fixes this.
  - One candidate is a relative jitter (`1e-8 * max(regularization_weights**2)`), but it changes
    evidence values. It is not filed.
  - The "~1 in 4 draws non-PD" figure is from the 512×512 runs. At 125×125 it was 0/20.

### (d) The routing cost model (#632)

- **Form.** The NumPy single-mapper interferometer inversion picks between the numba `direct_conv`
  curvature and the FFT route by predicted seconds:
  - `t_fft = c_fft · S · W_fft(2ny × 2nx)`, where `W_fft` is the rfft2 + irfft2 work of the padded
    extent, taken from scipy/pocketfft's own `cost_guess`.
  - `t_dc = c_dc · nnz · ny · nx`.
  - `c_fft` = 7.62e-10 and `c_dc` = 1.77e-09. Only the ratio decides the route.
- **Why factorization-aware.** 682 = 2·11·31 and 166 = 2·83 (pocketfft's Bluestein case) cost 2–5×
  more per element than 560 = 2⁴·5·7. In a micro-benchmark at padded lengths 140–682, seconds per
  model unit varied 1.8×, against 5.8× for seconds per `N log2 N`.
- **Calibration.** The constants come from a least-squares fit on log seconds over 9 paired
  single-thread timings: 6 bake-off cells from autolens_profiling#226 plus the 3 Aris 512 points. The
  model picks the faster route at 9/9. Measured/predicted ratio residuals are 0.68–1.47 (log-rms 0.26).
- **Extents.** The model uses the mask extent: 341² on the 512×512 mask and 83² on the 125×125 mask.
  682×682 is the padded FFT grid of the 341² extent, not the extent.
- **Implied crossovers.** About 51/58/58 nnz/col at the 70²/140²/280² bake-off extents (measured
  ~60 Delaunay, ~77 rectangular). About 166 at 341², where the measured crossover lies between 106
  and 188. About 309 at 83², where only points at ≤ 11.7 nnz/col were measured.
- **Settings.**
  - `interferometer_numba_nnz_per_source_max: null` (the new packaged default) uses the cost model.
  - A positive value is a hard gate, with its old meaning.
  - `0` is the kill switch for numba.
  - `interferometer_route: "numba" | "fft"` forces a route for A/B runs.
  - Revert by setting the gate back to `60.0`.
  - See [the decision record](../decisions/interferometer-route-gate-cost-model.md).

### (e) Phase-2 after-measurement (autolens_profiling#420, PR-open, not merged)

Copied from `results/notes/interferometer_route_gate_aris_2026_10.md` at head `32372865` of
[autolens_profiling#420](https://github.com/PyAutoLabs/autolens_profiling/pull/420), on PyAutoArray
`17caf228` with default settings and one fixed parameter vector.

- The route was observed live, from the inversion class.
- The measured s/call columns are earlier laptop medians on PyAutoArray `ccddfba6`, from before the
  three fixes. They were not re-timed.

| Mask (extent) | Vertices | nnz/col | Route chosen | Pred. t_fft/t_dc | Measured FFT s | Measured direct_conv s | JAX jit s | log-det numba | log-det JAX | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 125×125 (83²) | 1,405 | 11.7 | direct_conv | 26.4 | not measured | 0.396 | 1.96 | 2468.4463180 | 2468.4463180 | 3.9e-8 |
| 125×125 (83²) | 2,947 | 5.57 | direct_conv | 55.5 | not measured | 2.08 | 6.84 | 4350.2973995 | 4350.2973995 | 2.1e-8 |
| 125×125 (83²) | 5,526 | 2.98 | direct_conv | 103.7 | not measured | 6.12 | 12.0 | 10157.1564483 | 10157.1564483 | 4.0e-8 |
| 512×512 (341²) | 1,459 | 187.6 | FFT | 0.89 | 28.3 | 38.4 | 18.3 | 2573.1669411 | 2573.1669411 | 4.1e-8 |
| 512×512 (341²) | 2,577 | 106.2 | direct_conv | 1.57 | 44.1 | 34.2 | 32.2 | 4610.2972527 | 4610.2972526 | 2.6e-8 |
| 512×512 (341²) | 5,746 | 47.7 | direct_conv | 3.49 | 97.3 | 41.2 | not run | 10625.0105708 | 10625.0105708 | 4.4e-8 |

The faster measured arm is chosen in 6/6 cells. The record states two limits:
1. **The 512 agreement is in-sample.** The three 512 timing pairs are among the nine calibration
   points of the model, so agreement there is a fit check, not evidence that the model generalises.
2. **The 125 FFT arm is a proxy.** The NumPy FFT arm was never timed on the 125 mask. The comparison
   there is against the JAX-jit FFT route on 2.8–3.6 cores.

The six cells alone would also be routed correctly by a constant gate of about 150. The case against
a constant rests on the model's extent dependence (crossovers ~309 at 83² and ~166 at 341²), not on
these cells.

### (f) Remaining levers, ranked

| Rank | Lever | Size | State |
|---|---|---|---|
| L1 | One `cho_factor` of F+H for both the reconstruction solve and the log det (NumPy path, `use_positive_only_solver=False`). The positive-only path already reuses its factor. | 65 ms vs 113+81 ms at 1,405; 612 ms vs 948+654 ms at 2,947 → **−20% / −40–45% per call**. Solution change 7e-14 / 2e-11 relative, log det identical, non-PD still raises. | Filed and **in development**: Mind task `reuse-cholesky-factor`, PyAutoArray [#633](https://github.com/PyAutoLabs/PyAutoArray/issues/633). |
| L2 | `direct_conv` symmetry: rank the source columns by top extent row (`ymin`). Each column convolves only the extent rows that later-ranked columns span, clipped to each row's mask x-range. Gather the ranked upper triangle, then mirror. Computed entries are bit-identical. Serial numba only. | Real Aris 512, RAL quiet core: **1.49× / 1.53× / 1.58×** at 1,459 / 2,577 / 5,746 vertices (f 0.511 / 0.504 / 0.495). Synthetic Aris-512: 1.83–1.90× (f ≈ 0.41). Gain over the *previous default route* at 1,459 is only ~1.02×, because FFT measures 15.32 s on the same node. | **PR-open** [PyAutoArray#636](https://github.com/PyAutoLabs/PyAutoArray/pull/636) (issue #635; pending release; merge is the human's). Default gate 0.7. Record: autolens_profiling [#425](https://github.com/PyAutoLabs/autolens_profiling/pull/425) `results/notes/interferometer_direct_conv_symmetric_2026_10.md` (PR-open). Decision: [`direct-conv-symmetric-gate`](../decisions/direct-conv-symmetric-gate.md). |
| L3 | Fixed-mapper curvature preload: F, D, the mapper and the split mappings do not change while the lens is fixed, which is exactly a source_pix[1]-style phase with only AdaptSplit parameters free. | With L1: ~0.1 s at 1,405 (~6×), ~0.8 s at 2,947, ~1 s at 512 / 2,577 against 34–44 s (~30×). Applies to **fixed-lens phases only**; a moving lens (mass[1]) has nothing to cache. | Existing Pulse task `interferometer_fixed_mapper_curvature_preload` (ready; needs the fixed-mapper science decision). |

Not worth it (measured on the 125×125 setup unless stated):
- **float32 factor.** 2× faster, but a 0.027 nats log-det error at 2,947 vertices, with cond(F+H) up
  to 7e12. Not safe.
- **numba threads inside the worker processes.** 4 threads gave 2.7× at 1,405 and ~1.4× at 2,947 in
  one process. With 28 single-thread processes filling the node, the threads add nothing. They help
  only if memory forces fewer processes.
- **Delaunay, H and positions.** Each is under 3% of the call: Delaunay 2–3% (DelaunayNN is 43×
  slower), H build and log det ≤ 2%, positions likelihood 0.3%. numba compile is about 1.5 s once per
  worker.
- **BLAS swap.** ≤ 1.3×.
- **Positive-only solver.** 1.5–3× slower on this setup. Keep `use_positive_only_solver=False`.

### (g) Runtime settings for collaborators that matter

- **1 thread per process.** Pin the numba and BLAS threads to 1 and fill the node with processes.
  Put `NUMBA_CACHE_DIR` on node-local scratch.
- **`n_batch` a multiple of the worker count.** For example, 112 or 84 for 28 workers instead of 100,
  for about 10% throughput. The collaborator's runner was set to `n_batch = 4 × cores`.
- **Vertex count.** It is the cost lever above about 2k vertices: 0.63 s at 1,405 against 2.0–2.4 s at
  2,947. At 5,746 the two factorizations alone take about 12 s. Keep moving-lens phases (mass[1]) at
  about 1.4–2k vertices until L1 lands.
- **512×512.** At 1,459 vertices on the FFT route, this was the cheapest measured cell. The cost model
  now routes it automatically.
- **Leave `interferometer_numba_nnz_per_source_max` unset** (the cost model) unless running an A/B.
  Scripts that set it explicitly keep the old hard-gate meaning.
- **Leave `interferometer_direct_conv_symmetric_max_work_fraction` unset** (default 0.7) once
  PyAutoArray#636 is released. With serial numba it speeds up F by about 1.5× on multiply imaged
  sources at no accuracy cost. Set it to `0` only for an A/B test against the full kernel.

### (h) The symmetric `direct_conv` kernel and the tall-column insight (PyAutoArray#635 / #636, 2026-10-17)

- **Rule.**
  - The serial numba `direct_conv` route uses `curvature_direct_conv_symmetric` when the geometry
    work fraction f ≤ 0.7. f is computed from the mapper triplets and the mask extent in about 1 ms,
    before any curvature work.
  - Its time is κf of the full kernel, with κ = 1.32. κ was fitted on the synthetic geometry
    (log-rms 0.008) and checked out of sample on real data: predicted 1.48–1.53×, measured
    1.49–1.58×. So the kernel wins while f < 0.76.
  - The #632 route model scales `t_dc` by `min(1, κf)`.
- **Tall columns from multiple imaging.**
  - On real Aris data, each source vertex is fed by two to four lensed images, so its image-plane
    column spans a median of **90 of 341** extent rows (p95 158), against 15 on the synthetic
    3-NN geometry.
  - The tall columns are not the mask-edge vertices: 0 of the 30 tallest are edge vertices.
  - Tall columns overlap in rows, so less work can be skipped. f is about 0.50 on real data against
    about 0.41 synthetic, which means about 1.5× rather than 1.9×.
  - Ranking columns by **ascending `ymin`** instead of centroid lowers real-data f from 0.587 to
    0.511. On compact columns the ordering barely matters (0.416 → 0.414).
- **Witness.**
  - **Setup:** RAL `euclid-ral-compute-1`, `ral`, `--exclusive`, 1 thread, load ≤ 1.0, compile
    excluded, min of 2. Software: PyAutoArray `e59d5fa9` + v3 (PR head `62a1e3ac`), Nerves `7f3055b`,
    Fit `9b394e73`, Galaxy `9f9ac947`, Lens `4723668a`; numba 0.65.1, numpy 2.2.6.
  - **Curvature step:** 22.43 → 15.08 s (1,459 vertices), 22.83 → 14.95 s (2,577), 24.22 → 15.35 s
    (5,746).
  - **log L:** bit-identical at 1,459, relative 3e-16 at 2,577 and 2e-12 at 5,746.
  - **5,746 log det:** Δ 0.0071 nats, which is round-off. Control job 412493: the full kernel's own
    F, factorised from its lower versus its upper triangle, moves the log det by 0.0077 nats at
    cond(F+H) = 7.2e13.
  - **Memory:** peak RSS 43 GB without NUFFT chunking.
  - **Jobs:** 412490 (step 8 + synthetic), 412491 (FFT arm), 412492 (steps 6 and 4), 412493
    (control).
- **Route-constant calibration gap (deferred).**
  - At 1,459 vertices on RAL, FFT/full `direct_conv` measures **0.68**. The laptop-calibrated #632
    constants (`c_fft` 7.62e-10, `c_dc` 1.77e-09) predict 0.89.
  - The route the factory now picks at 1,459 (symmetric `direct_conv`, 15.08 s) is right, but only
    by about 1.02× over FFT (15.32 s). No measured route is wrong; the margin is thin on RAL.
  - A cluster-node refit of `c_fft / c_dc` is deferred: the human closed the interferometer CPU lane
    (human decision 2026-10-17, chat).
- **Not covered.**
  - The parallel numba kernel (unchanged).
  - The 125×125 mask, not re-timed with v3. The earlier research found the overhead cancels the
    gain there.
  - Other lenses: one real dataset only.
  - κ near the 0.7 gate: the predicted 1.08× there is an extrapolation.

### Check-in 2026-10-17

- **Released.** PyAutoArray#630, #631, #632 and #634 shipped in 2026.10.16.1 (2026-10-16); 2026.10.16.2 and 2026.10.17.1 contain no further PyAutoArray change. Earlier "pending release" wording above is historical.
- **Project records.** autolens_profiling#420 (phase-2 routing table under the cost model + log-det parity, issue #419) merged 2026-10-15 22:55Z; #422 (gate-60 wording marked historical, Pulse knowledge linked) and #424 (lint re-pin of abstract.py anchors and shared-Cholesky route probe after #634) merged 2026-10-16. Project main `fd29902`.
- **L1 (#634), measured on the NumPy path (PyAutoPulse#62 comment 2026-10-15T23:28Z).** solve+log-det 144.5 → 50.9 ms at 1,405 vertices; 1,268 → 373 ms at 2,947; full call −22–24% / −51%. Reconstruction within conditioning (cond 7.7e14), log det bit-identical, logL ≤ 1.1e-11.
- **L2 (PyAutoArray#635), paused by the human 2026-10-16.** Uncommitted on worktree `feature/direct-conv-symmetric` (base `e59d5fa9`), no PR. Serial numba, `euclid-ral-compute-1`, load < 1, A-C-C-A order, synthetic Aris-512 geometry (341² extent, 91,361 pixels, nnz 274,083): library kernel v2 (RAL 411835) 1.81× / 1.85× / 1.90× at S 1,428 / 2,540 / 5,712, spreads ≤ 1.004, computed entries bit-identical, full matrix differs only by the full kernel's own asymmetry (≤ 1.3e-15). Real Aris data on the laptop: columns are tall (median span 90 of 341 rows, likely multiple imaging), work fraction 0.587 (centroid order) / 0.511 (ymin order); measured full 40.4 s vs 30.5 s / 27.6 s = 1.32× / 1.46×; κ = 1.32 model predicts 1.29× / 1.48×. Jobs 411833/411834/411835 COMPLETED on `ral` (411832 FAILED after 11 s, superseded).
- **Human decision 2026-10-16 (recorded on #635, not yet a Pulse decision record):** rank columns by ascending ymin; raise the default `interferometer_direct_conv_symmetric_max_work_fraction` from 0.5 to 0.7 (kernel predicted to win while κf < 1, f < 0.76). v3 implementing this is in the worktree diff (gate 0.7, ymin ordering); its test run is unconfirmed.
- **Owed on resume (from the #635 checkpoint):** verify v3 and the full suites; RAL real-data witness on `ral`, serial (`l2_realdata.py --n-pixels 512 --mesh-step 8 --repeats 2`), gate ≥ 1.3× on the curvature step with matching logL; re-confirm the synthetic witness with ymin order; Heart check; `/ship_library` PR; write-up (autolens_profiling results note with the decision rule, this Knowledge section, decision record `direct-conv-symmetric-gate`). When L2 ships, the #632 `c_dc` constant is effectively scaled by min(1, κf) and the Aris-512 1,459-vertex cell is predicted to flip from FFT to direct_conv.
- **RAL staging verified 2026-10-17.** `/mnt/ral/jnightin/scratch/aris_l2_20261016/` holds `aris_data/`, `PyAutoArray` and `PyAutoArray_l2` (the v3 patch still to be applied), PyAutoNerves/PyAutoFit/PyAutoGalaxy/PyAutoLens mains, `numba_cache/`, the witness scripts, patches and the 411832–411835 job outputs.

## Check-in 2026-10-17 (evening)

- **L2 shipped to PR.** [PyAutoArray#636](https://github.com/PyAutoLabs/PyAutoArray/pull/636) (issue #635, head `62a1e3ac`, pending-release) and autolens_profiling [#425](https://github.com/PyAutoLabs/autolens_profiling/pull/425) (results note `results/notes/interferometer_direct_conv_symmetric_2026_10.md`): both OPEN, CI green, unmerged. Heart read STALE ("release validation incomplete: no rehearsal for current source"); no override used. Merge #425 after #636.
- **RAL real-data witness met** (≥ 1.3× on the curvature step): 1.49× / 1.53× / 1.58× at 1,459 / 2,577 / 5,746 vertices, predicted 1.48× / 1.50× / 1.53×; see Knowledge (h). Synthetic ymin order 1.83× / 1.86× / 1.90×.
- **Decision record** [`direct-conv-symmetric-gate`](../decisions/direct-conv-symmetric-gate.md) added for the human decision of 2026-10-16 on PyAutoArray#635 (ymin ordering, gate 0.5 → 0.7).
- **Human decision 2026-10-17 (chat):** interferometer CPU work is exhaustive and closed. The route-constant refit (RAL FFT/full `direct_conv` 0.68 measured vs 0.89 predicted) is deferred, not filed. Curvature preload (L3) parked: "we will come back to it soon".
- **State:** all L-levers are shipped or parked. This task stays active only until #636 and #425 are merged and released; merge is the human's.
