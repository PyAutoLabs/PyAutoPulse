# PyAutoPulse

The **Pulse** organ of the [PyAuto organism](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/ORGANISM.md):
where the organism feels how fast it runs.

**Board:** <https://pyautolabs.github.io/PyAutoPulse/>

PyAutoPulse is the cross-project profiling dashboard over the `<lib>_profiling`
project repos (today [autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling)).
It owns:

- the **instance registry** (`registry.yaml`) — which projects publish a
  profiling summary, where, under which contract version; each project is named
  by its PyAutoMind body-map identity, never a second repository catalogue;
- the versioned **`profiling-summary` read contract** — v1 is live at
  `autolens_profiling/dashboard/summary.json`, documented in that repo's
  [dashboard/README.md](https://github.com/PyAutoLabs/autolens_profiling/blob/main/dashboard/README.md);
- the **ingest receipts** (`receipts/`) — the one commit each project was read
  at, per render — and the last-good **snapshots** (`snapshots/`), shown as
  *cached* when a later fetch fails;
- the cross-project **Pages board** (`dashboard.md`, `dashboard.html`, plus
  `state.json` for the Brain cockpit and `badge.json`).

It validates the exchange contract only. It never moves pins, combines unmatched
timings, applies the compile threshold to runtime, computes an ecosystem-wide
speed score or issues a release-health verdict, and it never judges a timing —
the Brain's profiling conductor does (`/profiling triage <comparison_key>`). The
project repos keep their producers, results, drift policy and their own Pages page.

## Run it

Python 3.11+ with PyYAML; no scientific library is imported. A PyAutoMind
checkout supplies the body map (`--mind PATH`, `$PYAUTO_MIND`, or beside this
repo).

```bash
bin/pyauto-pulse check      # ingest at one resolved commit, validate, write receipts → "check: OK"
bin/pyauto-pulse board      # ingest, then render the board
bin/pyauto-pulse census     # one line per instance from the committed snapshots
bin/pyauto-pulse fetch --instance lens
pytest -q tests             # hermetic: no network
```

Formats, the contract as read and every rule: [REFERENCE.md](REFERENCE.md).
Boundaries: [AGENTS.md](AGENTS.md). Design:
[profiling_inference_organs.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/research/profiling_inference_organs.md).

## License

MIT — see [LICENSE](LICENSE).
