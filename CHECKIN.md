# All profiling work in one chat

The editable prompt at the top of the dashboard is the entry point. Direction
supplied before or after it has the same meaning: focus that campaign or assess
that idea while retaining the overall sweep. No direction means check all open
campaigns and tasks. This static page does not run jobs or monitor them itself.

## Check-in procedure

1. Fetch current Pulse, Mind and relevant project branches; read their agent
   instructions. Read `campaigns.yaml`, task files and `migration.yaml` when an
   old Mind path is referenced. Pulse is the canonical profiling queue.
2. Read each campaign's current project wiki/ledger, results and issue/PR state.
   Evidence URLs pin the last reviewed source; inspect the current default
   branch for subsequent changes too. Consult Brain's profiling conductor for
   scientific interpretation. With HPC access, use project pull/status commands;
   otherwise report which jobs/results remain unverified. Never infer completion
   from an old job id or absent data.
3. Compare with the last check-in and report one table: changes, current state,
   blockers, next bounded step. Keep timing, correctness, compile cost, memory
   and hardware distinct. Respect task contracts, human decisions, release gates
   and Mind's current repository claims.
4. Incorporate user direction into priorities and suggested next steps. An idea
   is a hypothesis until tested. Choose one bounded phase before execution and
   use existing development/compute authorization rules. The check-in itself
   authorizes no job submission, default/baseline change, release or merge.
5. Update `campaigns.yaml` with verified facts, reviewed dates, next steps and
   source links. Preserve parked/blocked work. Append decisions and their
   evidence to the task or project ledger. Record `last_checkin` as an ISO UTC
   timestamp after the sweep, noting unavailable sources in the affected tasks.
   A board refresh alone must never stamp a check-in.
6. Run `bin/pyauto-pulse board --offline` (or live ingest when available), then
   `bin/pyauto-pulse check --offline`; persist through the repo development
   workflow. Report the PR and whether it merged. Continue subsequent profiling
   requests in this conversation; a fresh chat resumes from these records.

## Ownership and development handoff

Pulse owns campaign intent and pending tasks. File new profiling work under
`tasks/` with a row in `campaigns.yaml`. Each task has a stable ID, campaign,
title, status, priority, path, reviewed date and next step. Campaigns carry a
title, status, reviewed date, next step and evidence URL. Completed/superseded
rows remain in the ledger but leave the open table. Parked and blocked work
stays visible. A campaign is not a job: active does not mean running.

For a library/workspace implementation phase, file a small Mind development
prompt referencing the Pulse task, then use start_dev and the normal issue/PR
and claim lifecycle. Reuse existing issues (including autolens_profiling#362 for
timing-noise audit). Do not copy entire campaigns into Mind or bulk issue their
phases. After close-out, link the completion record from the Pulse task and
update its next step. Mind retains repository claims and implementation PR
lifecycle; mixed science/library work stays there with Pulse links.

Projects retain detailed campaign evidence, producers, results, pins and drift
policy. Pulse scheduling metadata never changes measurement qualification or
Heart readiness. Migration preserves original text and provenance; historical
headers inside those texts are not a live queue. Resolve old Mind paths via
`migration.yaml`; use the pinned source commit for unmigrated historical paths.

## Record a key decision

When the user says "record this decision" or explicitly flags a key campaign
decision, use `decisions/README.md` to produce a high-level campaign summary.
Read the relevant campaign/task history and cited project/Cortex evidence;
preserve hardware, dataset, model and cold/warm-start distinctions. Summarize
the evidence, alternatives, the human's choice and its implications, with
source links and limitations. Do not infer an accepted choice from timings,
a passing run, or an agent recommendation. If the user is still deciding,
prepare a draft and ask for the missing choice before adding a history entry.

Write one canonical Markdown record in the campaign-leading organ and link it
from `decisions.yaml` on each relevant board. Do not categorize by repository
or dataset and do not duplicate the prose. Explicit direction to record a
stated decision authorizes the capture; ask only about genuinely missing facts.
Keep scientific sources authoritative and cite them. Preserve old decisions;
a changed choice receives a new dated record with supersession links.
Publish the owning record before adding its cross-dashboard link, verify the
GitHub destination, regenerate and check both affected boards through the
normal development workflow. Recording a decision does not authorize its
implementation or compute. Never turn an illustrative title into a decision.
