Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autolens_profiling/interferometer_streaming_scaling.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: streaming phases 3–5 merged Sep 30–Oct 1: PyAutoArray [#589](https://github.com/PyAutoLabs/PyAutoArray/pull/589), [#593](https://github.com/PyAutoLabs/PyAutoArray/pull/593), [#597](https://github.com/PyAutoLabs/PyAutoArray/pull/597), [#599](https://github.com/PyAutoLabs/PyAutoArray/pull/599), [#601](https://github.com/PyAutoLabs/PyAutoArray/pull/601); PyAutoLens #758/#761/#762; PyAutoGalaxy #639. #589/#593/#601 are in release 2026.10.2.1. Mind has `complete/2026/10/streaming-p5-cubes-phase-centre.md` ("phase 5 of 5").
- The go/no-go on phases 3–5 is overtaken by events.
- VERIFIED: the scaling measurement is unrun: no `scripts/interferometer/streaming_scaling/` and no `results/streaming_scaling/` on autolens_profiling `a93f37a`.
- Unverified: Discussion https://github.com/orgs/PyAutoLabs/discussions/13 not fetched.
- Next: the scaling measurement needs compute authorization from the human.

### Execution 2026-10-04

- Issue: [autolens_profiling#368](https://github.com/PyAutoLabs/autolens_profiling/issues/368). Branch `feature/interferometer-streaming-scaling` @`4a0ef46`, parked at Heart RED.
- Results (laptop CPU, 8 threads, indicative): chunk 65536 wall 17.5 / 43.8 / 180.7 / 504.5 s at 1e6 / 4e6 / 1.6e7 / 5e7 visibilities, RSS 1.47–1.69 GB; chunk 4096 wall 43.6 / 149.2 / 608.6 s at 1e6 / 4e6 / 1.6e7.
- In-memory first failure at 1e6 under a 10 GB cap (both arms). The `nufft_chunk_size` arm fails in `transformer.image_from`: a second memory wall, library candidate, no issue filed.
- Parity 1.2e-9 nats at 5e5. The 1e8 row was skipped (budget).
- Go/no-go overtaken; recorded as release evidence for 2026.10.4.1.

## Check-in 2026-10-07

- https://github.com/PyAutoLabs/autolens_profiling/pull/375 (issue #368) merged 2026-10-04T20:49Z: phase 1 CPU cells + results/streaming_scaling rows; https://github.com/PyAutoLabs/autolens_profiling/blob/719459fefb40c7e5be157f652818dbf923830557/wiki/campaigns/interferometer_streaming.md.
- Optional next: 1e8 CPU row and A100 rows (compute authorization). Library candidate still unfiled: chunk transformer.image_from in apply_sparse_operator.

---

# Campaign: interferometer streaming (array-free) vs in-memory — memory and time scaling to 2e8 visibilities

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Themes:
- interferometer
- sparse-operator
- memory
Difficulty: small
Autonomy: supervised
Priority: high
Status: draft
Consequence: glance
Witness: `scripts/interferometer/streaming_scaling/` holds the campaign cells (accumulator time scaling vs N_vis and chunk size; in-memory `apply_sparse_operator` pushed to failure under a memory cap; streaming at the failing sizes; log_evidence parity), each writing a versioned JSON row under `results/streaming_scaling/` through `_profile_cli.py`; `build_readme.py --check`, `check_results_layout.py`, `check_wiki.py` and `ruff` pass; `wiki/campaigns/interferometer_streaming.md` (from `_template.md`) records the table, the 2e8 extrapolation and the go/no-go on the streaming epic's remaining phases; the dashboard is regenerated.
Review-minutes: 5
Unattended: ready
Epic: streaming-visibilities

Source: the 2026-09-30 go/no-go question on Discussion https://github.com/orgs/PyAutoLabs/discussions/13 (HRSAstro's 2e8-sample ALMA cube). Phases 1-2 of the streaming epic are merged (PyAutoArray#593, PyAutoGalaxy#639, PyAutoLens#758). A scratchpad run of this benchmark was made in the CLI session on 2026-09-30 (`bench_stream.py`); this campaign ports it into the repo so the evidence is versioned and re-runnable per release.

## Scratchpad result to reproduce (2026-09-30)

In-memory `apply_sparse_operator` OOMs at 1e6 visibilities under a 10 GB cap (3.1 GB allocation in `nufft_precision_operator_via_nufft_from`; 2.1 GB peak already at 1e5). Streaming at chunk 65536: 16 / 52 / 174 / 539 s at 1e6 / 4e6 / 1.6e7 / 5e7 (≈11 s per 1e6 vis, linear), peak RSS 1.5–1.8 GB flat; chunk 4096 is 5× slower (per-chunk fixed cost: nufft spread 46 %, JAX recompiles ~73 across 40 chunks, device→host copies). 2e8 ⇒ ~37 min, ~1.8 GB. Verdict GO; the table is on the epic ledger.

## Why

The array-free dataset only earns its maintenance cost (a second dataset kind every interferometer code path branches on) if it makes a real difference at the visibility counts real data reach. In-house datasets are ≤1.1e5 visibilities; the discussion's case is 2e8. The decision on phases 3-5 (visualizer, non-linear light profiles, cubes) rests on measured crossover memory and on the accumulator being linear and fast enough to reach 2e8.

## What

1. Cells under `scripts/interferometer/streaming_scaling/` (dataset-first, task-second layout; use `_profile_cli.py` for JSON/CLI; synthetic seeded per-chunk visibilities generated in memory, 400-px circular mask at 0.05"/pix, `TransformerNUFFT`; each measurement in a fresh child process with a `RLIMIT_AS` cap and per-child timeout):
   - `accumulate.py` — `Interferometer.from_stream` wall time and peak RSS vs N_vis ∈ {1e6, 4e6, 1.6e7, 5e7} × chunk ∈ {4096, 65536}; seconds per 1e6 vis; linearity.
   - `in_memory.py` — `Interferometer(...).apply_sparse_operator()` peak RSS + wall at N_vis ∈ {1e6, 4e6, 1.6e7, 5e7, 1e8}; the first N that fails under the cap is a result.
   - `parity.py` — log_evidence of a 20×20 rectangular sparse inversion, streamed vs in-memory at 4e6.
2. `results/streaming_scaling/` rows + PNG (RSS and wall vs N_vis, both paths) following `check_results_layout.py`; README dashboard via `build_readme.py`; `build_dashboard.py` regenerated.
3. `wiki/campaigns/interferometer_streaming.md` from `_template.md`: table, 2e8 extrapolation (in-memory RSS ≈ 96 B/vis + temporaries vs streaming RSS; accumulation time at the best chunk), a cProfile top-10 of one chunk if any rate exceeds 5 s per 1e6 vis, and the go/no-go for the epic's phases 3-5. Link from `wiki/index.md`.
4. A100 rows (RAL) are optional follow-ups; CPU rows decide the memory question.

Parallel claims: autolens_profiling is claimed by `raw-pdip-forward-polish` (`interferometer-decision-matrix` shipped 2026-09-30, `complete/2026/09/interferometer-decision-matrix.md`); this campaign adds a new task folder and results folder only (shared files: `wiki/index.md` rows + generated README/dashboard).
