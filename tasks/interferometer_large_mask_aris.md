# Interferometer large-mask likelihood — memory and routing (Aris 512×512)

Campaign: interferometer
Task: interferometer_large_mask_aris
Reviewed: 2026-10-15
Status: active

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
