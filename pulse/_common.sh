#!/usr/bin/env bash
# pulse/_common.sh — shared helpers + globals for every Pulse module.
#
# Source this file. It sets:
#
#   PULSE_HOME           — repo root (PyAutoPulse/)
#   PULSE_STATE_DIR      — ~/.pyauto-pulse/ (created on first call)
#   PULSE_PER_REPO_DIR   — per-repo JSON caches
#   PULSE_TIMINGS_DIR    — rolling script timing baselines
#   PULSE_LOG_DIR        — daemon log files
#   PULSE_PID_FILE       — daemon pidfile
#   PULSE_STATE_FILE     — aggregated latest snapshot
#   PYAUTO_ROOT          — ~/Code/PyAutoLabs/ (where the repos live)
#
# And the helper functions:
#
#   pulse_log <level> <msg>      — timestamped log line to stdout and PULSE_LOG_DIR/pulse.log
#   pulse_state_dir              — ensure state dir tree exists
#   load_repos_yaml              — print the list of polled repos as `owner/name` lines
#   load_repos_by_group <group>  — print just one group's repos
#   pulse_with_lock <name> <cmd> — flock-style serialisation for state writes

set -u   # nounset; tolerate unset only in explicit checks via ${VAR:-}

# Determine PULSE_HOME by walking up from this file.
_pulse_common_self="${BASH_SOURCE[0]}"
PULSE_HOME="$(cd "$(dirname "$_pulse_common_self")/.." && pwd)"
export PULSE_HOME

PYAUTO_ROOT="${PYAUTO_ROOT:-$HOME/Code/PyAutoLabs}"
export PYAUTO_ROOT

PULSE_STATE_DIR="${PULSE_STATE_DIR:-$HOME/.pyauto-pulse}"
PULSE_PER_REPO_DIR="$PULSE_STATE_DIR/per-repo"
PULSE_TIMINGS_DIR="$PULSE_STATE_DIR/timings"
PULSE_LOG_DIR="$PULSE_STATE_DIR/logs"
PULSE_PID_FILE="$PULSE_STATE_DIR/pulse.pid"
PULSE_STATE_FILE="$PULSE_STATE_DIR/state.json"
PULSE_TICK_LOG="$PULSE_LOG_DIR/pulse.log"
export PULSE_STATE_DIR PULSE_PER_REPO_DIR PULSE_TIMINGS_DIR PULSE_LOG_DIR
export PULSE_PID_FILE PULSE_STATE_FILE PULSE_TICK_LOG

source "$PULSE_HOME/pulse/_color.sh"

pulse_state_dir() {
  mkdir -p "$PULSE_STATE_DIR" "$PULSE_PER_REPO_DIR" "$PULSE_TIMINGS_DIR" "$PULSE_LOG_DIR"
}

# Live-mode detection. Live (clear-screen, redraw, countdown) when stdout is a
# terminal; plain (streamed, append-only) otherwise — e.g. when an agent runs
# the daemon or output is piped to a file. Override with PULSE_LIVE=1 (force
# live) or PULSE_LIVE=0 (force plain).
pulse_is_tty() {
  case "${PULSE_LIVE:-}" in
    1) return 0 ;;
    0) return 1 ;;
  esac
  [ -t 1 ]
}

# Clear screen + home cursor (only meaningful on a tty).
pulse_clear_screen() {
  printf '\033[H\033[2J'
}

# Log to stdout (coloured by level) and to PULSE_TICK_LOG (plain).
pulse_log() {
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date -Iseconds)"

  local stdout_line stderr_line
  case "$level" in
    DEBUG) stdout_line="$(c_meta "[$ts] DEBUG") $msg" ;;
    INFO)  stdout_line="$(c_info "[$ts] INFO ") $msg" ;;
    OK)    stdout_line="$(c_ok   "[$ts] OK   ") $msg" ;;
    WARN)  stdout_line="$(c_warn "[$ts] WARN ") $msg" ;;
    FAIL)  stdout_line="$(c_fail "[$ts] FAIL ") $msg" ;;
    *)     stdout_line="[$ts] $level $msg" ;;
  esac

  printf '%s\n' "$stdout_line"
  pulse_state_dir
  printf '[%s] %s %s\n' "$ts" "$level" "$msg" >> "$PULSE_TICK_LOG"
}

# Print "owner/name group" for every polled repo, one per line.
# Uses Python because parsing YAML in bash is fragile.
load_repos_yaml() {
  local config="${1:-$PULSE_HOME/config/repos.yaml}"
  python3 - "$config" <<'PY'
import sys
import yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
for group, entries in data.get("repos", {}).items():
    for repo in entries:
        print(f"{repo['owner']}/{repo['name']} {group}")
PY
}

# Same as load_repos_yaml but for a single group only.
load_repos_by_group() {
  local group="$1"
  local config="${2:-$PULSE_HOME/config/repos.yaml}"
  load_repos_yaml "$config" | awk -v g="$group" '$2 == g {print $1}'
}

# Simple file-based lock for state cache writes. Usage:
#
#   pulse_with_lock state '
#     ... commands that write $PULSE_STATE_FILE ...
#   '
pulse_with_lock() {
  local name="$1"; shift
  pulse_state_dir
  local lock="$PULSE_STATE_DIR/$name.lock"
  (
    flock -x 200
    eval "$@"
  ) 200> "$lock"
}

# Atomic JSON write: write to a tempfile, then rename.
pulse_write_json() {
  local target="$1"
  local content="$2"
  local tmp
  tmp="$(mktemp "${target}.XXXXXX.tmp")"
  printf '%s\n' "$content" > "$tmp"
  mv "$tmp" "$target"
}
