#!/usr/bin/env bash
# pulse/daemon.sh — foreground watch loop. Calls tick.sh on a schedule.
#
# Usage: bash pulse/daemon.sh [interval_seconds]
#
# Default interval: 300s (5 min). Ctrl+C exits cleanly.

set -u
source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/_common.sh"

interval="${1:-${PULSE_INTERVAL:-300}}"

pulse_state_dir

# Pidfile guard.
if [[ -f "$PULSE_PID_FILE" ]]; then
  existing="$(cat "$PULSE_PID_FILE" 2>/dev/null)"
  if [[ -n "$existing" ]] && kill -0 "$existing" 2>/dev/null; then
    pulse_log FAIL "$(c_fail "pyauto-pulse already running with pid $existing — refusing to start")"
    pulse_log INFO "$(c_meta "stop it with: pyauto-pulse stop")"
    exit 1
  else
    pulse_log WARN "$(c_warn "stale pidfile $PULSE_PID_FILE (pid $existing not running) — overwriting")"
  fi
fi
echo $$ > "$PULSE_PID_FILE"

cleanup() {
  rm -f "$PULSE_PID_FILE"
  pulse_log INFO "$(c_info "daemon stopped")"
}
trap cleanup EXIT INT TERM

pulse_log OK "$(c_bold "PyAutoPulse daemon started")  $(c_meta "(pid $$, interval ${interval}s)")"

while true; do
  bash "$PULSE_HOME/pulse/tick.sh"
  pulse_log INFO "$(c_meta "sleeping ${interval}s until next tick…")"
  sleep "$interval"
done
