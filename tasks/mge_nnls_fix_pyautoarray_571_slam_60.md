Migrated-from: https://github.com/PyAutoLabs/PyAutoMind/blob/f21898e042be67afd86cc9c512879b3ad1c9ca9a/draft/research/autoarray/mge_nnls_fix_pyautoarray_571_slam_60.md
Migrated-at: 2026-10-03

The original task below is retained verbatim. Current scheduling state lives in `campaigns.yaml`; historical `Status` and paths below are provenance, not a second queue. Resolve old Mind paths through `migration.yaml`.

## Check-in 2026-10-04

- VERIFIED: [PyAutoArray#595](https://github.com/PyAutoLabs/PyAutoArray/pull/595) merged 2026-09-30 (`7a89e19a`) and is an ancestor of tags 2026.10.2.1 (first release) and 2026.10.4.1. The release half of the blocker is met.
- Unverified: the RAL mirror sync via HPCPullPyAuto; no record since 2026-10-02. Also diff the RAL venv's dependency floors, not only library hashes.
- Context: jax-version policy changes (e.g. PyAutoArray#612) merged to mains 2026-10-04, unreleased; a mirror sync now pulls them too. Mind epics.md still says "#595 pending release" (stale).
- Next: a CLI session runs HPCPullPyAuto and records the synced hashes; then this task can flip to ready.

### Execution 2026-10-04

- RAL sync SKIPPED 2026-10-04: 180 euclid_dr1 tasks RUNNING with `PYAUTO_HPC_BASE=/mnt/ral/jnightin/PyAuto` on PYTHONPATH.
- Mirror at 2026-09-27 state (Nerves `bf10410231`, Fit `404b3e5f77`, Array `9428eca24a`, Galaxy `c960982566`, Lens `21b520be4d`), 16–35 commits behind tag 2026.10.4.1.
- HPCPullPyAuto pulls MAINS, and Nerves main excludes jax 0.10.2 (installed on RAL and locally), so a sync also needs a jax reinstall.
- Next: sync when `squeue -u jnightin -t R` shows no euclid_dr1 jobs on the shared base, or the human accepts the risk.

## Check-in 2026-10-07

- RAL 2026-10-07 ~18:40Z: `squeue -u jnightin` showed 0 RUNNING, 0 PENDING (one probe). The 2026-10-04 blocker condition (no euclid_dr1 jobs on the shared base) is met.
- Three later probes timed out: shared mirror /mnt/ral/jnightin/PyAuto HEAD/tag UNVERIFIED.
- Human decision (same day, in chat): **never** HPCPullPyAuto the shared mirror while euclid_dr1 depends on it. Phase 3 runs from a private RAL checkout at tag 2026.10.7.1 (contains PyAutoArray#595) with its own environment; Nerves at that tag excludes jax 0.10.* and RAL has jax 0.10.2, so the private env needs a compliant jax. Status → `ready`; compute for the A100 rows still needs separate authorization.

### Execution 2026-10-07 — phase 3a shipped

- Human approved the phase-3a plan and the A100 job in chat; issue [autolens_profiling#393](https://github.com/PyAutoLabs/autolens_profiling/issues/393), PR [#394](https://github.com/PyAutoLabs/autolens_profiling/pull/394) merged 2026-10-07T21:18Z (`a55dcacb`).
- Private base `/mnt/ral/jnightin/PyAuto_wt/linear-solver-p3/` at tag 2026.10.7.1 (Nerves c5ade605, Fit 710f4b34, Array ccddfba6, Galaxy b4946b8a, Lens b6bf543c); A100 job 397475 on euclid-ral-gpu-1, 1:04, jax/jaxlib 0.10.2; shared mirror untouched.
- Parity (81 systems, fp64, vs stored fnnls references): released `pdip_raw` CPU vs A100 max |Δ flux_inactive_rel| 5.4e-14, max |Δ amp_rel_max_sig| 4.0e-10, iterations identical 81/81; inadmissible under the pre-registered rule on both devices (phase-2 reasons). `pdip_jacobi` diverges 29 (CPU) vs 19 (A100); `pdip_raw_tol_jaxnnls` flips one flag at the cap. Median warm wall (context only): 0.88 ms CPU, 3.96 ms A100 unbatched.
- Record: PyAutoMind `complete/2026/10/linear-solver-p3a-a100-parity.md`. Phase 3b draft: `draft/research/autolens_profiling/linear_solver_phase3b_gpu_timing_cell.md`. Status → `active` (3b pending).

## Check-in 2026-10-08

- VERIFIED: autolens_profiling main at `a55dcacb` (#394 merge); no later commits, PRs or issues touching the solver corpus. Pulse ledger PR #34 open, lint + refresh green, mergeable, unmerged.
- VERIFIED: Mind draft `draft/research/autolens_profiling/linear_solver_phase3b_gpu_timing_cell.md` committed in `208bac7b` (2026-10-07 22:20 +0100) with the phase-3a record. Phase 3b not yet through start_dev; no issue, branch or claim exists.
- RAL (one probe, 2026-10-08): euclid_dr1 arrays 397467 and 397469–397474 RUNNING/PENDING on `ral` against the shared base, so the 2026-10-07 "0 jobs" window has closed; the private base `/mnt/ral/jnightin/PyAuto_wt/linear-solver-p3/` still holds the five library clones. `/mnt/ral/jnightin/autolens_profiling/results/lens/solver/` does not exist — where job 397475 wrote its JSON on RAL is unverified (the rows are committed in #394).
- Next (unchanged): start_dev for phase 3b; A100 rows need separate compute authorization. Nothing here authorizes a submit.

### Execution 2026-10-08 — phase 3b delivered (PR open)

- Human approved the plan and one A100 submit in chat. Issue [autolens_profiling#395](https://github.com/PyAutoLabs/autolens_profiling/issues/395); PR [#396](https://github.com/PyAutoLabs/autolens_profiling/pull/396) open (commits b8911d8, e68448c, d7b6e1e), lint pending at review time. Mind `active/linear_solver_phase3b_gpu_timing_cell.md`, worktree `linear-solver-p3b-gpu-timing`.
- New cell `scripts/lens/solver/timing.py` (jit(vmap) over `_solvers.batched_kernel`; SLaM batches = distinct fixture+slam48 systems, euclid lanes tiled). A100 job 398249 on euclid-ral-gpu-2 (0:38) from the private base; RAL sibling worktree `/mnt/ral/jnightin/autolens_profiling_wt/linear-solver-p3b` created because the p3 one held untracked (byte-identical) 3a artefacts. Shared mirror untouched.
- Per-evaluation min ms (7 interleaved rounds, fp64, tag 2026.10.7.1 SHAs verified in both JSONs): pdip_raw SLaM CPU 1.353/0.881/0.682, A100 3.948/0.581/0.190 at B=1/16/50; pdip_jacobi SLaM CPU 2.488/1.630/1.396, A100 6.715/1.149/0.369. Compile walls 0.3–1.2 s recorded separately. Batched pdip_raw matches unbatched on every lane (|Δ flux_inactive_rel| ≤ 1.4e-14).
- Slowest-lane mechanism confirmed: jacobi batch max iterations sit at the 50 cap when any lane diverges (A100 B=16/50), costing 1.94x pdip_raw at A100 B=50. New, unexplained: jacobi batched vs unbatched trajectories differ on the A100 (19/50 lanes iterations, 13/50 flags), identical on CPU.
- Caveats: euclid lanes tiled (throughput only); A100 used the warm shared JAX compile cache; laptop under background load (loadavg ~1.9); CPU batched run on jax 0.10.2 (Nerves-excluded, no deadlock seen). Verdict in the ledger: a timing is not admissibility; no pin moves.
- Next: human /prm on #396 → Mind completion record → Pulse task status; then the programme-level decision.

### Close-out 2026-10-08 — phase 3b merged, phase 4a issued

- autolens_profiling#396 merged 2026-10-08T08:26Z (`86cb1460`), every CI leg green; issue #395 closed; Mind record `complete/2026/10/linear-solver-p3b-gpu-timing.md` (Mind d43d3864); laptop worktree removed; Pulse ledger PR #35 merged.
- Human decision (chat 2026-10-08): run phase 4 as research and keep the write-up in the wiki for a future decision. Filed and issued as [autolens_profiling#397](https://github.com/PyAutoLabs/autolens_profiling/issues/397) (phase 4a: localise the A100-only jacobi batched/unbatched divergence — determinism, vmap lowering vs lane count, tiled lanes, first-differing iteration via `max_iter=k`, cond(Q) join; wiki/research page with a decision table; one A100 job authorized). Mind `active/linear_solver_phase4_jacobi_a100_batched_divergence.md` (cff6e8e6), worktree `linear-solver-p4a-jacobi-a100-divergence`. 4b (corpus widening, kernel-selection probes, flag experiments) deferred unless 4a leaves it open.

---

# Linear-solver programme phase 3: GPU/vmap/A100 timing and parity rows for the solver corpus

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: too-large
Autonomy: supervised
Priority: medium
Memory: wiki/lensing/sources/dark-matter-substructure.md; reading-queue.md; wiki/lensing/sources/lens-modeling-methods.md
Status: formalised
Filed: 2026-09-24, retargeted: 2026-09-30 (epic linear-solver-programme)
Blocked-by: a release shipping the phase-2 fix (PyAutoArray#595, merged 2026-09-30 pending release; record complete/2026/09/raw-pdip-forward-polish.md) AND the RAL mirror synced via HPCPullPyAuto
Witness: `scripts/lens/solver/timing.py` rows plus `accuracy.py --device gpu` rows on the phase-1 corpus (`results/lens/solver/corpus/`: slam_fixture_571, slam48_hst, slam_spread_hst, euclid_vis_lp — 81 systems) record, for the SLaM source_lp[1] 60-column model and the captured euclid system, single / vmap16 / vmap50 per-evaluation cost on the RTX 2060 and RAL A100 fp64 for jacobi vs raw (released phase-2 solver), the NNLS share of each batch, and GPU-vs-CPU parity (max |dlogL| and amplitude/`flux_inactive_rel` agreement) on the 48 near-truth vectors — appended to `results/notes/linear_solver_accuracy_2026_09.md` and `wiki/campaigns/linear_solver_accuracy.md`.
Review-minutes: 3
Consequence: glance
Unattended: needs-slicing

Epic `linear-solver-programme`, phase 3. Contract: `complete/2026/09/linear-solver-accuracy-study.md` (phase-1 record with the original programme prompt folded in).

This prompt was filed on 2026-09-24 as a standalone PyAutoArray#571 follow-up (SLaM 60-column GPU
timing and parity, single and vmap). The original ask below now lives in the phase-1
`scripts/lens/solver/` package and its corpus rather than in a fresh
`scripts/imaging/hazards/` script: the SLaM model recipe, the 48 near-truth vectors and the
euclid capture are already corpus systems, so phase 3 adds GPU/A100 cells to that package and
appends rows to the shared ledger. Phase 1 found the released raw stop leaves spurious
amplitude on reference-inactive columns while logL barely moves, so GPU parity must be scored
with `flux_inactive_rel` (and amplitude agreement), not logL alone.

## Context

Context: the 2026-09-24 audit measured only CPU timing for the fix (neutral: 27.3 -> 25.8 ms single, 31.3 -> 30.3 ms/eval vmap16). On GPU the pre-fix behaviour made every Nautilus vmap batch run all 50 PDIP iterations whenever one lane failed (NNLS ~28% of a 2060 batch, ~44% of a single A100 evaluation), so the fix should cut batch cost; that is unmeasured. GPU parity of the raw-forward PDIP is also unmeasured (the audit saw CPU/GPU/vmap divergence on the failing vectors pre-fix).

## Ask

1. Add a new cell to `scripts/lens/solver/timing.py` following the package's `_driver`
   pattern, loading the SLaM source_lp[1] 60-column system and the euclid capture from
   `results/lens/solver/corpus/`; time single, vmap16 and vmap50 per-evaluation cost on the
   RTX 2060 and RAL A100, fp64, with `nnls_preconditioning_no_mapper` forced to jacobi and to
   raw (the released phase-2 solver), interleaved minima.
2. Record NNLS share per config via the existing solve ablation pattern (unconstrained solve
   swap) or `stats["iterations"]`.
3. GPU parity: run `accuracy.py --device gpu` over the corpus (at minimum the 48 near-truth
   vectors); report max |logL_gpu - logL_cpu|, amplitude agreement and `flux_inactive_rel`
   against the CPU fnnls reference, and iterations per lane.
4. Append the rows and a verdict to `results/notes/linear_solver_accuracy_2026_09.md` and
   `wiki/campaigns/linear_solver_accuracy.md` (regenerate README dashboards,
   `build_readme.py --check`); route any regression to /intake as a bug.

<!-- formalised by the Intake (Conception) Agent on 2026-09-24; retargeted into epic linear-solver-programme phase 3 on 2026-09-30 -->
