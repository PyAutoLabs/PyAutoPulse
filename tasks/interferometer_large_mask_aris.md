# Interferometer large-mask likelihood — memory and routing (Aris 512×512)

Campaign: interferometer
Task: interferometer_large_mask_aris
Reviewed: 2026-10-15
Status: active (all three library members merged 2026-10-15, pending release; phase-2 record and Aris log-det after-measurement in flight)

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

The autolens_profiling phase-2 record is in flight. It re-measures the routing table under the cost
model and records the Aris log-det after-measurement. Copy that table here, then close the task.
