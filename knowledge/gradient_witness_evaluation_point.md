# Gradient witness: where the evaluation point sits matters

Status: knowledge. Written 2026-11-02 for
[autolens_profiling#515](https://github.com/PyAutoLabs/autolens_profiling/issues/515), after
[PyAutoArray#671](https://github.com/PyAutoLabs/PyAutoArray/issues/671). Evidence and the per-cell
table are in the research note (at its first commit)
[gradient_campaign_impact_border_tie.md](https://github.com/PyAutoLabs/autolens_profiling/blob/9af783c97922293a1ebc9f528e26c916f1a133c8/wiki/research/gradient_campaign_impact_border_tie.md).
Pulse records this; it does not apply, detect or enforce anything.

## Rule

Before trusting or distrusting a `gradient.json` FD verdict, check **where it was evaluated**.
An evaluation point that sits on a symmetry of the problem can make autodiff disagree with
finite differences for reasons that say nothing about the likelihood in general.

- **Lens centred exactly on the mask's symmetry centre (pixelized source, border relocator on).**
  Before PyAutoArray#672, the border relocator's ellipse extent was a `max` over exactly tied
  ± border pairs, and under `jit` its reverse-mode gradient came out 2x or 0.5x the true value.
  Cells evaluated like this on a library older than #672's release are suspect.
- **Odd grid at pixelization over-sampling 1, with the mass centre exactly on a grid point** (HST
  141x141 at the prior medians). The Isothermal `psi` softening (a 1e-8 core) makes the true
  derivative with respect to the centre about 1e8 at that point. Autodiff is right for the softened
  profile, and no FD step can see it. Move the evaluation point off the grid rather than treating
  this as a bug.
- **The phase-6 campaign cells are clear of both.** Every pixelized cell is a `--standard-size` cell
  evaluated at iid draw 0 of the seeded production sequence, whose mass centre is a generic value
  near 0, not 0. The non-pixelized cells at the prior medians have no border relocator, and the MGE
  imaging cells hold the mass fixed. One cell was re-run before and after #672 and gave a
  bit-identical gradient.

## Reading a `gradient.json`

- The `point` field is unreliable on the standard cells: every standard driver except the group
  and multi-galaxy one records `prior_medians` although it evaluates at iid draw 0.
- A pixelized `no_plateau` verdict comes from the FD sweep alone. A library fix that leaves values
  unchanged (as #672 does) cannot move it.
- Compare the stored autodiff with the stored central difference at the smallest sweep steps
  (1e-8 to 1e-6). Agreement there means the autodiff matches the local likelihood; a disagreement
  at every small step, on a cell whose gradient is not tiny, is worth a closer look.
