# PyAutoPulse

The **Pulse** organ of the [PyAuto organism](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/ORGANISM.md):
where the organism feels how fast it runs.

PyAutoPulse is the cross-project profiling dashboard over the `<lib>_profiling`
project repos (today [autolens_profiling](https://github.com/PyAutoLabs/autolens_profiling)).
It owns:

- the **instance registry** — which projects publish a profiling summary, where,
  under which contract version;
- the versioned **`profiling-summary` read contract** — v1 is live at
  `autolens_profiling/dashboard/summary.json`;
- the **ingest receipts** — the resolved commit per project per render;
- the cross-project **Pages board**.

It validates the exchange contract only. It never moves pins, combines unmatched
timings, applies the compile threshold to runtime, computes an ecosystem-wide
speed score or issues a release-health verdict, and it never judges a timing —
the Brain's profiling conductor does. The project repos keep their producers,
results, drift policy and their own Pages page.

**Status:** stub. The registry, reader, receipts, board and workflows arrive in
phase 2 of the `profiling-organ-birth` epic. Design:
[profiling_inference_organs.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/research/profiling_inference_organs.md).

## License

MIT — see [LICENSE](LICENSE).
