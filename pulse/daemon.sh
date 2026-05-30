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

# A live countdown that redraws a single line each second (tty only). Falls
# back to a plain sleep when not live.
pulse_countdown() {
  local secs="$1"
  if pulse_is_tty; then
    local remaining
    for (( remaining = secs; remaining > 0; remaining-- )); do
      printf '\r%s' "$(c_meta "next tick in ${remaining}s …   ")"
      sleep 1
    done
    printf '\r%*s\r' 40 ''   # clear the countdown line
  else
    pulse_log INFO "$(c_meta "sleeping ${interval}s until next tick…")"
    sleep "$secs"
  fi
}

while true; do
  if pulse_is_tty; then
    pulse_clear_screen
    printf '%s\n\n' "$(c_bold "PyAutoPulse · live")  $(c_meta "· $(date -Iseconds) · every ${interval}s · Ctrl-C to stop")"
  fi

  # Run one refresh. tick.sh streams its per-check / per-repo progress so the
  # work is visible as it happens.
  bash "$PULSE_HOME/pulse/tick.sh"

  # In live mode, render the dashboard after the tick (forced colour even
  # though the countdown writes to the same tty). In plain mode the streamed
  # tick output is the record; rendering again would just duplicate it.
  if pulse_is_tty; then
    printf '\n'
    PULSE_FORCE_COLOR=1 PYTHONPATH="$PULSE_HOME" python3 -m pulse.status || true
  fi

  pulse_countdown "$interval"
done
