#!/usr/bin/env bash
# pulse/checks/repo_state.sh — per-repo branch + dirty + behind/ahead check.
#
# Runs `git fetch` (cheap) and porcelain queries in parallel across all
# polled repos. Writes one JSON file per repo at
# $PULSE_PER_REPO_DIR/<name>.repo_state.json and prints a one-line
# coloured summary per repo to stdout (for the daemon log).

set -u
source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../_common.sh"

check_one_repo() {
  local owner_name="$1"
  local group="$2"
  local name="${owner_name##*/}"
  local repo_path="$PYAUTO_ROOT/$name"

  if [[ ! -d "$repo_path/.git" ]]; then
    pulse_write_json "$PULSE_PER_REPO_DIR/$name.repo_state.json" "$(printf '{"name":"%s","present":false,"group":"%s"}' "$name" "$group")"
    pulse_log WARN "$(c_warn "$name") — repo missing on disk"
    return
  fi

  local branch dirty ahead behind upstream
  branch="$(git -C "$repo_path" branch --show-current 2>/dev/null)"
  branch="${branch:-(detached)}"
  dirty="$(git -C "$repo_path" status --porcelain 2>/dev/null | wc -l)"
  upstream="$(git -C "$repo_path" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "")"

  # Fetch silently before computing ahead/behind so the numbers are fresh.
  git -C "$repo_path" fetch --quiet origin 2>/dev/null || true

  if [[ -n "$upstream" ]]; then
    local counts
    counts="$(git -C "$repo_path" rev-list --left-right --count "$upstream"...HEAD 2>/dev/null || echo "0	0")"
    behind="${counts%%[[:space:]]*}"
    ahead="${counts##*[[:space:]]}"
  else
    behind="0"; ahead="0"
  fi

  local ts
  ts="$(date -Iseconds)"

  pulse_write_json "$PULSE_PER_REPO_DIR/$name.repo_state.json" "$(python3 -c "
import json
print(json.dumps({
    'name': '$name',
    'group': '$group',
    'present': True,
    'branch': '$branch',
    'dirty_files': $dirty,
    'ahead': $ahead,
    'behind': $behind,
    'upstream': '$upstream',
    'ts': '$ts',
}))
")"

  # One-line summary.
  local glyph dirty_str ahead_str behind_str branch_str
  if [[ "$dirty" -eq 0 && "$ahead" -eq 0 && "$behind" -eq 0 && "$branch" == "main" ]]; then
    glyph="$(glyph_ok)"
    branch_str="$(c_meta "$branch")"
    dirty_str=""; ahead_str=""; behind_str=""
  else
    glyph="$(glyph_warn)"
    if [[ "$branch" != "main" ]]; then branch_str="$(c_warn "$branch")"; else branch_str="$(c_meta main)"; fi
    if [[ "$dirty" -gt 0 ]]; then dirty_str=" $(c_warn "dirty=$dirty")"; else dirty_str=""; fi
    if [[ "$ahead"  -gt 0 ]]; then ahead_str=" $(c_warn "ahead=$ahead")"; else ahead_str=""; fi
    if [[ "$behind" -gt 0 ]]; then behind_str=" $(c_warn "behind=$behind")"; else behind_str=""; fi
  fi
  printf '%s %s %s%s%s%s\n' "$glyph" "$(c_info "$name")" "$branch_str" "$dirty_str" "$ahead_str" "$behind_str"
}

check_repo_state_all() {
  pulse_state_dir
  pulse_log INFO "$(c_info "repo_state: scanning $(load_repos_yaml | wc -l) repos")"
  while read -r line; do
    [[ -z "$line" ]] && continue
    local owner_name group
    owner_name="${line%% *}"
    group="${line##* }"
    check_one_repo "$owner_name" "$group" &
  done < <(load_repos_yaml)
  wait
  pulse_log OK "$(c_ok "repo_state: done")"
}

# Allow running standalone.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  check_repo_state_all
fi
