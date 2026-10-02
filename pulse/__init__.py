"""PyAutoPulse: the cross-project profiling dashboard organ.

The ``<lib>_profiling`` project repos run their profiling producers, keep their
results and drift policy, and each one publishes a ``profiling-summary`` file.
This package reads the instance registry (``registry.yaml``), resolves each
instance's repository through the PyAutoMind body map, reads its summary at
one resolved commit, validates the exchange contract, writes an ingest receipt
and builds the board (``dashboard.md`` + ``dashboard.html`` + ``state.json``).
It recomputes no ratio, moves no pin, combines no unmatched timings and judges
nothing: judgment belongs to the Brain's profiling conductor.
"""

from pathlib import Path

ORGAN_ROOT = Path(__file__).resolve().parents[1]
