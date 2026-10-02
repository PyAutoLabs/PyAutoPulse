# PyAutoPulse — reference

The registry schema, the `profiling-summary` v1 contract as this organ reads
it, and the formats of the receipts, snapshots, board markers and cockpit feed.
Prose boundaries live in [AGENTS.md](AGENTS.md); the design is
[profiling_inference_organs.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/research/profiling_inference_organs.md).

## Registry (`registry.yaml`, `schema: 1`)

One row per instance under `instances:`. Unknown fields are refused.

| Field | Required | Meaning |
|---|---|---|
| `instance` | yes | Stable key within the organ, `^[a-z][a-z0-9_-]*$`, unique. |
| `repo` | yes | A PyAutoMind body-map identity (`repos.yaml` key). `path` and `github` are read from the body map at load time and **may not** be written in the row. |
| `summary_path` | yes | Repository-relative path of the producer's summary (no `/`-prefix, `..`, URL). |
| `supported_schema` | yes | `<schema>@<integer version>` the reader expects, e.g. `profiling-summary@1`. |
| `dashboard_url` | yes | The project's own human-facing page (`https://`). |
| `library_refs` | no | Body-map identities the project exercises (each must be in the body map). |
| `cortex_project` | no | An existing Cortex key, or `null`. |

Further rules: the same `(repo, summary_path)` may be registered once (disjoint
scopes; no inflated coverage). Every ingest reads branch `main`.

Body map resolution order: `--mind PATH` (must hold `repos.yaml`, never a
silent fall-through), `$PYAUTO_MIND`, `$PYAUTO_ROOT/organs/PyAutoMind`,
`$PYAUTO_ROOT/PyAutoMind`, then beside this organ (grouped `organs/` or flat
task-bundle layout). No body map → an error, never a guess.

## `profiling-summary` v1, as read here

The producer documents the contract
([autolens_profiling `dashboard/README.md`](https://github.com/PyAutoLabs/autolens_profiling/blob/main/dashboard/README.md));
this is what `pulse/summary.py` enforces. Additive fields are ignored.

**Support.** `(schema, version)` must be `("profiling-summary", 1)` *and* match the
registry row's `supported_schema`; otherwise the outcome is **unsupported** and
nothing else is validated.

**Envelope** — required: `schema, version, project, scope, generated_at,
evidence_updated_at, producer_revision, comparison_policy, coverage, records,
comparisons, limitations`. A missing field makes the feed **invalid**.

- `project`, `scope`: non-empty strings.
- `generated_at`: ISO-8601 UTC (`Z` or `+00:00`).
- `evidence_updated_at`: ISO-8601 UTC, or `null` with a non-empty
  `evidence_updated_at_reason`.
- `valid_until` (optional): `null` (= freshness policy unspecified) or ISO-8601
  UTC not before `evidence_updated_at`.
- `producer_revision`: 40-hex or `null` — the producer *code* revision, distinct
  from the commit the organ resolved (which the receipt records).
- `comparison_policy`: an object with a non-empty `id`.
- `coverage`: `expected` object; `observed` object of non-negative integers;
  `excluded` list of `{id, reason, evidence: {path}}` with safe paths.
- `limitations`: list of non-empty strings, shown verbatim.

**Records** — each an object with:

- `id`: non-empty, unique in the file (grammar `<series key>@<release reference>`).
- `axis` ∈ `runtime | compile | breakdown | memory`, and `unit` belongs to its axis
  (`s` for the time axes; `B/KB/MB/GB/KiB/MiB/GiB` for memory). A memory unit in a
  seconds series — or the reverse — is refused.
- `measurement`: non-empty object of finite numbers or `null`, at least one non-null
  (`NaN`/`inf`/booleans refused).
- `identity`: object carrying `device`, `backend`, `precision` (values may be
  `null`; absence is an error).
- `provenance`: object with boolean `has_provenance` and `qualified`, a `host`
  key (null if unknown); numeric fields finite. A record with
  `has_provenance: false` is shown and counted **unqualified**, never dropped.
- `evidence.path`: repo-relative (no leading `/`, `..`, `\`, URL); resolved
  against the commit the organ captured.

**Comparisons** — each an object with a unique non-empty `comparison_key`,
`policy` equal to `comparison_policy.id`, `axis` in the axis table, a `metric`,
`status` ∈ `drifted | improved | flat | insufficient`, finite-or-null `ratio`,
boolean `qualified`, `reasons` list of strings, `baseline`/`candidate` a release
reference or `null`.

**Pairing (display rule, not a feed error).** Each comparison's endpoints
resolve to records `<comparison_key>@<baseline>` / `@<candidate>`. A pair is
**refused by the reader** — listed apart with its reason, ratio not shown —
when an endpoint is not among the records, when the records' axes differ from
each other or from the comparison's, or when their hardware identity
(`device`, `backend`, `precision`, `host`) differs. A host is compared only when
both records name one. Accepted pairs are grouped by `device · backend ·
precision`, in producer order (never sorted by ratio).

**Outcomes.** `ok` · `invalid` (not JSON, or contract breaks) · `unsupported`
(schema/version) · `unavailable` (transport: API or raw file unreadable).

## Ingest

1. `GET https://api.github.com/repos/<owner>/<repo>/commits/main` → one 40-hex SHA
   (stdlib `urllib`, 20 s timeout, `User-Agent`, `Authorization: Bearer $GH_TOKEN`
   on API calls only, when set).
2. `GET https://raw.githubusercontent.com/<owner>/<repo>/<sha>/<summary_path>`.
3. Validate; write the receipt; on `ok` also write the snapshot.

`--offline` reads the committed receipt + snapshot and writes nothing. `--from
[INSTANCE=]PATH` reads a local checkout (or the file), reports its `HEAD` and
dirty state (`git status --porcelain`), is labelled "local checkout", and
writes **no** receipt or snapshot.

### Receipt — `receipts/<instance>.json`

```json
{
  "instance": "lens", "repo": "autolens_profiling", "github": "PyAutoLabs/autolens_profiling",
  "branch": "main", "resolved_commit": "<40-hex or null>", "summary_path": "dashboard/summary.json",
  "source": "remote", "fetched_at": "<UTC Z>", "outcome": "ok|invalid|unavailable|unsupported",
  "schema": "profiling-summary", "version": 1, "record_count": 159,
  "errors": [], "cached_from": "<last good snapshot's fetched_at, when outcome != ok; else null>"
}
```

### Snapshot — `snapshots/<instance>.json`

`{instance, repo, github, summary_path, commit, fetched_at, summary}` — the last
good summary verbatim, with the commit and time it was captured. Written only on
an `ok` read; a failed read leaves it untouched, and the board shows it as
**cached** with its original `commit`, `fetched_at` and the summary's own
`evidence_updated_at`, plus the new receipt's error.

**Carried times.** A receipt or snapshot is rewritten only when something other
than `fetched_at` changes, so `fetched_at` is the time an outcome at a commit
was *first* observed. A nightly refresh against an unchanged project commits
nothing; a new project commit moves both.

## Board

- `dashboard.md` / `dashboard.html`: the project table (Project, Scope,
  Evidence, Last fetch, Coverage, **Integrity**, **Freshness**,
  **Qualification**, Links), then per instance the producer's
  limitations, excluded rows and comparisons by hardware group, each comparison
  linking its two records' evidence at the captured commit and carrying
  `/profiling triage <comparison_key>`. Freshness without a policy is shown as
  "freshness policy unspecified · age N d at fetch <date>" (the HTML adds a live
  "N d today"); a passed `valid_until` reads "stale".
- Instance marker (what `check` compares to the receipt):
  `<!-- pulse:instance name=<instance> receipt=<resolved commit|none> outcome=<outcome> shown=<snapshot commit|none> -->`.
- `badge.json`: shields endpoint, label `pulse`, message = the state headline.
- `state.json`: the Brain cockpit feed v1 (`PyAutoBrain/board/_state.py`):
  `organ: pulse`, `repo: PyAutoPulse`, `pages_url: https://pyautolabs.github.io/PyAutoPulse/`,
  headline `N project(s) · R records · C cached[ · F failed]`; `updated` moves only
  when the content does.

| Item | Severity |
|---|---|
| latest read `invalid`/`unsupported`, or `unavailable` with no capture | red |
| `unavailable` with a cached capture | yellow |
| `valid_until` passed; or no policy and evidence older than 90 d (presentation only) | yellow |
| valid empty feed ("no measurements") | yellow |
| records the producer marks unqualified | yellow |
| `drifted` comparison, qualified | yellow, with the triage action |
| `drifted` comparison, unqualified (a contextual flag) | info, with the triage action |
| local read; census line | info |

Status: red if any red item, else yellow if any yellow, else green. A drift
item's actions are `{id: triage, kind: prompt, safety: scientific_judgement,
target: "/profiling triage <comparison_key>"}` and a read-only link to the
candidate's evidence at the captured commit.

## CLI

| Command | Does |
|---|---|
| `check [--offline] [--from …] [--mind PATH]` | body map + registry valid; each instance ingests (online: resolves, fetches, writes the receipt) and validates; each receipt records its snapshot commit; dashboard markers match the receipts; `state.json` meets the Brain contract (validator found at `$PYAUTO_BRAIN`, else beside this organ). Prints `check: OK` / `check: FAIL`. |
| `board [--offline] [--from …] [--mind PATH]` | ingest, then write the four board files. |
| `census [--mind PATH]` | one line per instance from the committed snapshots: records · comparisons · limitations · qualified · integrity · commit. |
| `fetch [--instance K] [--mind PATH]` | ingest + receipt only; exit 1 when a fetch fails. |

## Workflows

- `lint.yml` — ruff, hermetic pytest, `check --offline` (Mind + Brain checked out), lychee.
- `dashboard_refresh.yml` — `repository_dispatch: pulse-refresh`, nightly 03:55 UTC,
  `workflow_dispatch`, push to main on `registry.yaml`/`pulse/**` (commit + push, 3
  attempts, then dispatch `pages_dashboard.yml`), and a no-commit dry run on PRs.
  Main writers share the concurrency group `pulse-main-writers`.
- `pages_dashboard.yml` — publishes `dashboard.html` as `index.html` with `badge.json`
  and `state.json`, after validating the feed with `PyAutoBrain/board/_state.py`.
