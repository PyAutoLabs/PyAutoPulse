# heart/shell/heart_prompt.sh — one-line vital sign on shell / venv activation.
#
# Source this from ~/.bashrc (or a venv activate script) to print a single,
# instant health line from PyAutoHeart's CACHED state when a shell opens:
#
#     # ~/.bashrc
#     export PYAUTO_HEART_PROMPT=1                       # opt in (off by default)
#     source "$HOME/Code/PyAutoLabs/PyAutoHeart/heart/shell/heart_prompt.sh"
#
# Hard requirements (all satisfied here):
#   * Never runs a tick — reads the cache only, so it adds <100 ms and never
#     blocks the prompt.
#   * Never errors when state is absent/stale — degrades to a one-line hint
#     ("run pyauto-heart tick") instead of a traceback or non-zero exit.
#   * Honours NO_COLOR (the underlying renderer does).
#   * Opt-in via $PYAUTO_HEART_PROMPT so it never surprises anyone.
#   * Shows the board's age; the renderer flags staleness itself.
#
# The heavy lifting is the pure `dashboard --oneline` renderer; this file is
# only the sourceable glue.

# Print the one-line summary. Safe to call by hand: `heart_prompt`.
heart_prompt() {
  # Locate the CLI: prefer one already on PATH, else this file's own checkout.
  local heart
  if command -v pyauto-heart >/dev/null 2>&1; then
    heart="pyauto-heart"
  else
    local self src
    # BASH_SOURCE works when sourced; fall back to a well-known path otherwise.
    src="${BASH_SOURCE[0]:-}"
    if [ -n "$src" ]; then
      self="$(cd "$(dirname "$src")/../.." 2>/dev/null && pwd)"
      [ -x "$self/bin/pyauto-heart" ] && heart="$self/bin/pyauto-heart"
    fi
  fi
  [ -z "${heart:-}" ] && return 0   # Heart not installed here — say nothing.

  # `dashboard --oneline` reads cache only and self-degrades with no state, so
  # this can never block or error. Guard once more so a broken checkout is silent.
  "$heart" dashboard --oneline 2>/dev/null || true
}

# Auto-run on source, but only when explicitly opted in.
if [ -n "${PYAUTO_HEART_PROMPT:-}" ]; then
  heart_prompt
fi
