#!/usr/bin/env bash
# pulse/tick.sh — one-shot refresh: run every check, aggregate into state.json.
#
# Composable: run directly for a force-refresh, or via the daemon loop
# in pulse/daemon.sh. Each check writes its own JSON sidecar; the Python
# aggregator at the end reads them all into ~/.pyauto-pulse/state.json.

set -u
source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/_common.sh"

cd "$PULSE_HOME"

pulse_log INFO "$(c_bold "==== tick start") $(c_meta "($(date -Iseconds))") $(c_bold "====")"

# Run the four bash checks. Each is parallel-internal, so we run them
# sequentially for clean output, but they're cheap enough that this is
# fine (~5–10s total).
bash "$PULSE_HOME/pulse/checks/repo_state.sh"      || pulse_log WARN "$(c_warn 'repo_state failed')"
bash "$PULSE_HOME/pulse/checks/ci_status.sh"       || pulse_log WARN "$(c_warn 'ci_status failed')"
bash "$PULSE_HOME/pulse/checks/open_prs.sh"        || pulse_log WARN "$(c_warn 'open_prs failed')"
bash "$PULSE_HOME/pulse/checks/worktree_drift.sh"  || pulse_log WARN "$(c_warn 'worktree_drift failed')"

# Python: script timing regressions. Only runs if PyAutoBuild test_results/latest exists.
if [[ -d "$PYAUTO_ROOT/PyAutoBuild/test_results/latest" ]]; then
  PYTHONPATH="$PULSE_HOME" python3 -m pulse.checks.script_timing || pulse_log WARN "$(c_warn 'script_timing failed')"
else
  pulse_log INFO "$(c_meta 'script_timing: skipped (no PyAutoBuild/test_results/latest)')"
fi

# Aggregate into state.json.
PYTHONPATH="$PULSE_HOME" python3 -c "
from pulse import state
state.aggregate()
"

pulse_log OK "$(c_bold "==== tick complete") $(c_meta "(state at $PULSE_STATE_FILE)") $(c_bold "====")"
