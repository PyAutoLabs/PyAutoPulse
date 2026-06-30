#!/usr/bin/env bash
# heart/checks/ci_status.sh — per-required-workflow CI conclusions on main HEAD.
#
# For each polled repo this fetches, via `gh` (cheap metadata reads only):
#   1. the `main` HEAD commit sha   (`gh api .../commits/main`)
#   2. the recent workflow runs on `main` (`gh run list --branch main`)
# and pipes the runs JSON to `heart.checks.ci_status`, which picks the latest
# run of each workflow, rolls the *required* workflows for the repo's group
# (config/repos.yaml `required_workflows`) into one conclusion, writes the
# structured sidecar at $HEART_PER_REPO_DIR/<name>.ci_status.json, and prints
# the coloured one-line summary.
#
# This replaces the old `gh run list --limit 1` (newest run, ANY workflow, ANY
# branch) which could report a green url-check while smoke_tests was red. The
# heavier per-workflow detail is still just metadata — two cheap `gh` calls per
# repo, run in parallel — so the <30s tick budget holds.
#
# If `gh` is unavailable or a repo has no runs, the sidecar is written with an
# empty conclusion (dashboard shows "(no runs)"); the continuous tick degrades
# gracefully rather than failing.

set -u
source "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../_common.sh"

# Fields the Python roll-up needs from each run.
_CI_RUN_FIELDS="workflowName,name,conclusion,status,headSha,createdAt,url,event"

check_one_repo_ci() {
  local owner_name="$1"
  local group="$2"
  local name="${owner_name##*/}"

  local runs head_sha ts
  runs="$(gh run list --repo "$owner_name" --branch main --limit 30 \
        --json "$_CI_RUN_FIELDS" 2>/dev/null || echo '[]')"
  head_sha="$(gh api "repos/$owner_name/commits/main" --jq '.sha' 2>/dev/null || echo '')"
  ts="$(date -Iseconds)"

  printf '%s' "$runs" | PYTHONPATH="$HEART_HOME" python3 -m heart.checks.ci_status \
    --name "$name" --group "$group" --head-sha "$head_sha" --ts "$ts" \
    --out "$HEART_PER_REPO_DIR/$name.ci_status.json"
}

check_ci_status_all() {
  heart_state_dir
  heart_log INFO "$(c_info "ci_status: scanning $(load_repos_yaml | wc -l) repos via gh (per-required-workflow on main HEAD)")"
  while read -r line; do
    [[ -z "$line" ]] && continue
    local owner_name group
    owner_name="${line%% *}"
    group="${line##* }"
    check_one_repo_ci "$owner_name" "$group" &
  done < <(load_repos_yaml)
  wait
  heart_log OK "$(c_ok "ci_status: done")"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  check_ci_status_all
fi
