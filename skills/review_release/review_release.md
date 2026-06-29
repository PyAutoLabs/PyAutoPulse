# Review Release: Triage Release Readiness

Fetch the latest release build results, present a release readiness summary, and route to either release or fix. This is the "morning after" skill — run it after an overnight build to assess whether the software is ready for release.

A **PyAutoHeart** skill — release-readiness triage is exactly the health/readiness verdict Heart owns (`pyauto-heart readiness`). It reads the build results that PyAutoBuild produced; Build executes, Heart judges.

## Steps

### 1. Fetch Latest Release Run

Find the most recent release workflow run:

```bash
gh run list --workflow=release.yml --repo Jammy2211/PyAutoBuild --limit 5 --json databaseId,status,conclusion,createdAt,url
```

Present the runs and let the user pick one (default: most recent completed run). Show status and conclusion for each.

If the most recent run is still in progress, report its status and ask if the user wants to wait or review a previous run.

### 2. Download the Release Report

Download the `release-report` artifact from the selected run:

```bash
gh run download <run-id> --repo Jammy2211/PyAutoBuild --name release-report --dir /tmp/release-report
```

Read `release-report.json` and `release-report.md` from the downloaded artifact.

If the artifact doesn't exist (workflow predates this feature, or the `analyze_results` job didn't run), fall back to checking job statuses:

```bash
gh run view <run-id> --repo Jammy2211/PyAutoBuild --json jobs --jq '.jobs[] | {name, conclusion}'
```

### 3. Present Release Readiness Summary

Display the report in a clear format:

```
Release Readiness Report
========================

Status: READY / NOT READY
Run: <URL>
Date: <date>

Summary
-------
Passed: X | Failed: Y | Skipped: Z | Timeout: W

Per-Project Breakdown
---------------------
autofit:     P passed, F failed, S skipped
autogalaxy:  P passed, F failed, S skipped
autolens:    P passed, F failed, S skipped
autofit_test:    ...
autolens_test:   ...
```

### 4. Failure Analysis

For each failure, present:
- File path
- Classification (source code bug, workspace issue, environment, timeout, etc.)
- Error summary (first 2-3 lines)
- PR correlation (if the script was recently modified)
- Traceback snippet (collapsible)

Group failures by classification so the user can see patterns (e.g. "3 environment failures — all ModuleNotFoundError for the same package").

### 5. Check for Copilot Analysis

If a GitHub Issue was created by the build (labelled `ai-analysis`):

```bash
gh issue list --repo Jammy2211/PyAutoBuild --label "ai-analysis" --limit 5 --json number,title,url,comments
```

Fetch the most recent one matching this run. Check if Copilot has posted analysis comments:

```bash
gh api repos/Jammy2211/PyAutoBuild/issues/<number>/comments --jq '.[].body'
```

If Copilot analysis exists, summarise its key findings (root causes, recommendations, go/no-go).

### 6. Skipped Tests Review

Show the count of skipped tests and flag any that seem stale or risky:
- Scripts skipped due to known bugs — are those bugs still open?
- Scripts skipped due to missing features — has the feature been implemented?
- GUI scripts — always skipped, no action needed

### 7. Release Decision

Ask the user:

```
What would you like to do?

  (a) Release — all tests pass, proceed with release
  (b) Fix and rebuild — failures need fixing before release
  (c) Release anyway — accept known failures and proceed
  (d) Investigate — dig deeper into specific failures before deciding
```

#### If (a) Release:

Confirm the version number and that the `release` and `release_workspaces` jobs will execute. The release jobs in the workflow are already gated on test success, so if tests passed, they should have run. Verify:

```bash
gh run view <run-id> --repo Jammy2211/PyAutoBuild --json jobs --jq '.jobs[] | select(.name | startswith("release")) | {name, conclusion}'
```

If the release jobs completed successfully, report "Release complete" with the version number.

If the release jobs were skipped (because `skip_release` was true or tests failed), offer to re-trigger with release enabled.

#### If (b) Fix and rebuild:

Identify which failures need fixing and where the fix likely lives:
- **Source code bugs** → "Run `/start_library` to fix these in the library code"
- **Workspace issues** → "Run `/start_workspace` to fix these workspace scripts"
- **Environment issues** → "These may need workflow/dependency changes in PyAutoBuild"

Create a mini-prompt summarising the failures to give context for the next dev session. Write it to `PyAutoMind/release_fixes.md`:

```markdown
## Release Fix: <date>

### Failures to fix

1. `autolens/scripts/modeling/start_here.py` — AttributeError: 'FitImaging' has no attribute 'log_likelihood'
   - Classification: source_code_bug
   - Likely fix: check PyAutoLens FitImaging API changes

2. `autofit/scripts/searches/nest/UltraNest.py` — ModuleNotFoundError: No module named 'ultranest'
   - Classification: environment
   - Likely fix: add ultranest to optional requirements or update no_run.yaml

### Suggested approach
<brief recommendation based on failure patterns>
```

Tell the user: "Failure context written to `PyAutoMind/release_fixes.md`. Run `/start_dev` to begin fixing."

#### If (c) Release anyway:

Warn about the known failures. If `skip_release` was set to true in the original run, offer to re-dispatch with `skip_release=false`:

```bash
gh workflow run release.yml --repo Jammy2211/PyAutoBuild --field minor_version=<N> --field skip_scripts=true --field skip_notebooks=true --field skip_release=false
```

#### If (d) Investigate:

Ask which failure(s) to investigate. For each:
- Show the full traceback
- Show the relevant source code (read the failing script)
- Show recent git log for the file
- If PR-correlated, show the PR diff

Let the user explore until they're ready to choose (a), (b), or (c).
