Filed: 2026-11-06 (human decision in chat: "I think making critical curve thing use JAX for modeling runs with visualization makes sense to me" … "or doing work to figure out if its feasible")

# Feasibility: can the JAX zero-contour engine draw critical curves and caustics during modeling-run visualization?

Type: research
Target: autolens_profiling
Repos:
- @autolens_profiling
- @PyAutoGalaxy
- @PyAutoLens
Themes:
- critical-curves
- visualization
- jax
Difficulty: medium
Priority: medium
Campaign: critical-curves

## Question

Modeling runs draw critical curves and caustics on fit figures: in `fit_imaging_plots`, at quick-update and stage-end visualization. Today that uses `marching_squares` (`visualize/general.yaml: critical_curves_method`). PyAutoGalaxy already wires a JAX engine, `zero_contour` (`jax_zero_contour.ZeroSolver`, in `LensCalc.*_via_zero_contour_from` and `plot_utils._critical_curves_method`). Is `zero_contour` **correct and cheaper** for modeling-run visualization, at which scales, and with what seed policy and fallback?

## Evidence so far (this campaign)

- Phase 3a (2026-10-02, autolens_profiling#364): NO-GO for blindly routing *cluster* plots to zero-contour. The default ±3″ automatic seeds missed both cluster tangential curves, and an explicit far-source curve had a 20.65″ closing chord (path not completed). Galaxy-scale was not the subject.
- Phase 3b: the evaluation-grid cap preserves the field (PyAutoGalaxy#646).
- PyAutoLens#808: cluster plotting reads `critical_curves_method`.
- Docs drift: PyAutoGalaxy `plot_utils` docstrings call `zero_contour` the default, while the config default is `marching_squares`.

## Feasibility phase (bounded, research only, no default change)

1. **Correctness corpus.** The lifecycle day-zero datasets per scale: galaxy (imaging/hst, interferometer/sma), multi_galaxy/hst, group/euclid, cluster/simple, plus the phase-3a cluster witness. Evaluate on posterior draws from the phase-4 modeling runs (autolens_inference results), not only the truth, because modeling-run figures show fits away from the truth. Apply the pre-registered rule: every reference component found, each within two fine-grid pixels (0.1″ galaxy control, 0.25″ cluster), paths closed. Report seed coverage and path completion per scale.
2. **Cost in the modeling-run context.** Per-visualization call, both cold (including compile) and warm: marching squares (NumPy grid, and the JAX grid where used) against zero-contour, on CPU and A100, at the visualization cadence of a real run. Report the compile cost amortised over a run's visualizations, not just a single warm call.
3. **Failure detection and fallback.** Can an incomplete or missed curve be detected cheaply (e.g. curve count against the marching-squares coarse grid, closure check), so a fallback to marching squares is automatic?
4. **Outcome.** GO / NO-GO per scale, a recommended default plus seed and fallback policy, and the docs-drift fix. Any library or config change ships as its own later phase via start_dev.

## Notes

- Visualization cost only matters if it's a noticeable share of a modeling run's wall. The phase-4 walltime rows (autolens_inference#59) and the quick-update plotting cost task give the denominator.
