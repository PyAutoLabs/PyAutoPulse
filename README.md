# PyAutoPulse

Continuous-monitoring daemon for the PyAuto ecosystem.

## What it does

Polls 18 PyAuto repos every N minutes for:

- **Repo state** — branch / dirty / ahead / behind
- **CI status** — latest workflow conclusion per repo (via `gh run list`)
- **Open PRs** — count + max age, classified by staleness
- **Worktree drift** — `~/Code/PyAutoLabs-wt/` dirs vs `active.md` claims
- **Script timing** — per-script duration regressions vs a rolling baseline

Caches results to `~/.pyauto-pulse/state.json` for fast `status` reads.
Surfaces drift the day it appears instead of the day before a release.

All output is colour-coded:

- **green** — passing / clean / nominal
- **yellow** — warning / stale / mild drift
- **red** — failing / actionable now

`NO_COLOR=1` or `--no-color` strips colours for pipes / CI / redirection.

## Quick start

```bash
# Install (one time)
cd ~/Code/PyAutoLabs/PyAutoPulse
pip install -e .

# One-off refresh
pyauto-pulse tick

# Pretty-print the cached state
pyauto-pulse status

# Run the daemon in a tab (Ctrl-C to stop)
pyauto-pulse watch                 # default 300s interval
pyauto-pulse watch 60              # tick every 60s
PULSE_INTERVAL=120 pyauto-pulse watch
```

After PyAutoBuild#TBD lands, the same commands work via the unified CLI:

```bash
autobuild watch
autobuild status
autobuild tick
autobuild fix ci PyAutoFit
```

## Daily usage pattern

Open a WSL tab in the morning:

```bash
pyauto-pulse watch &
```

…and leave it running. Glance at the tab to see the current state.
When something turns red:

```bash
pyauto-pulse fix ci <repo>          # CI failure
pyauto-pulse fix drift              # worktree state
pyauto-pulse fix timing <project>   # script timing regressions
```

…emits a context bundle + Claude Code invocation you can paste/run.

## Architecture

```
bin/pyauto-pulse                 # dispatcher (mirrors autobuild's pattern)

pulse/
  _color.sh                      # ANSI helpers (bash side)
  pulse_color.py                 # ANSI helpers (Python side)
  _common.sh                     # shared globals + helpers
  daemon.sh                      # the foreground watch loop
  tick.sh                        # one refresh cycle
  state.py                       # atomic JSON cache I/O
  status.py                      # pretty-print cached state
  fix.py                         # emit Claude invocations on demand
  checks/
    repo_state.sh
    ci_status.sh
    open_prs.sh
    worktree_drift.sh
    script_timing.py

config/
  repos.yaml                     # the 18 polled repos + thresholds

tests/                           # pytest, runs in <1s
```

State cache at runtime:

```
~/.pyauto-pulse/
  state.json                     # aggregated latest snapshot
  pulse.pid                      # daemon pidfile
  per-repo/<name>.<check>.json   # per-repo sidecars
  timings/<workspace>__<dir>__<file>.json  # rolling per-script duration history
  logs/pulse.log                 # daemon stderr + tick events
  worktree_drift.json
  script_timing.json
```

## Configuration

`config/repos.yaml` lists the 18 polled repos and the classification
thresholds. To add or remove a repo, edit the file and restart the daemon
(`pyauto-pulse stop && pyauto-pulse watch`).

## Tests

```bash
pip install -e .[dev]
pytest tests/ -v
```

## Roadmap

- v2: desktop notification dispatch; smarter PR/issue checks; stash staleness
- v3: TUI panel (textual/rich) with hotkey drill-down
- v4: cross-machine sync (sqlite); team-shared cache

## Relationship to other PyAuto repos

- **PyAutoBuild** — provides the primitives (`autobuild run_all`, `autobuild url_check`, etc.). Pulse shells out to these but never imports PyAutoBuild Python.
- **PyAutoPrompt** — Pulse reads `active.md` for worktree drift detection (read-only).
- **admin_jammy** — Pulse sources `software/worktree.sh` for `PYAUTO_WT_ROOT` etc.

Pulse never writes to any other repo. State lives entirely under `~/.pyauto-pulse/`.
