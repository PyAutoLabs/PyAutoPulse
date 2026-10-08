# PyAutoPulse — reference

The [campaign control room](CHECKIN.md) provides one editable check-in prompt,
active campaigns and Pulse-owned tasks above the detailed profiling evidence.
`campaigns.yaml` is the scheduling ledger; `migration.yaml` records original Mind
prompts and their source commit. Board refreshes never change task status or stamp
a check-in. Run `bin/pyauto-pulse board --offline` after ledger edits.

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

## `profiling-summary` v2: setup catalogue

The v2 reader lands before the project producer migrates. Registry entries
still pin an exact version; supporting v2 does **not** silently upgrade the live
`profiling-summary@1` registry or reinterpret a saved v1 snapshot. The full
[synthetic fixture](tests/fixtures/setup_summary_v2.json) is an executable
producer example. Validation is stdlib-only in `pulse/catalogue.py`, through
`pulse.summary.classify`; it never opens evidence files or judges science.

V2 retains the common v1 envelope and receipt fields. It requires `setups`,
`records`, `selections`, `hazards`, and `recommendations` lists (empty is valid).
IDs are non-empty and unique within each list; references resolve within the
same document and project. `comparisons` must be `[]`: this catalogue presents
selected results, not release trends. Keep `comparison_policy.id` explicitly
labelled, e.g. `no-temporal-comparisons`, for common receipt/board compatibility.
The board provides an interactive setup browser over captured v2 evidence. Historical v1 feeds and their comparison rules remain
supported without rewriting measurements, pins, or policy.

### Setups

Each setup has `id`, `label`, `dataset`, `model`, `instrument`,
`configuration_id`, and a non-empty `configuration` object. IDs are semantic,
not script paths. A configuration ID identifies exact scientific settings;
changing solver, regularization, dataset or resolution requires a different
setup. Instrument is a string, or null with `unknowns.instrument` explaining
why (including dataset-independent component profiling).

Configuration fields are named objects with `value` and `unit`; examples are
`source_pixels: {value: 1500, unit: count}` and
`psf_shape: {value: [21, 21], unit: pixel}`. Use `name` for settings such as
solver and `dimensionless` where appropriate. A null value requires `reason`.
Include all scientifically relevant settings, not merely the instrument name;
legacy unknowns must remain unknown rather than inheriting today's defaults.
All nested metadata must be finite JSON; NaN and infinity are refused.

### Measurement records

Each record has:

- `id`, `setup_id`, `run_id`, `axis`, `metric`, `unit`, and `measurement`.
  Axes/units follow the v1 table. `measurement` contains **exactly one** key,
  equal to `metric`, with a finite non-negative value; booleans/null are not
  measurements. Missing cells belong in selections, not zero-valued records.
- `identity`: `device`, `backend`, `precision`, `library_version`, and a
  non-empty `software` mapping of measured package names to versions/revisions.
  Nullable identity fields require corresponding `identity.unknowns` reasons.
  Software captures the measured stack, not the current reader environment.
- `method`: `id`, `statistic`, positive integer `repetitions`, `warmup`,
  `synchronization`, and `cache_state`. Except for `id`, unknowns may be null
  with corresponding `method.unknowns` reasons. Reusing a method ID with a
  different method definition is invalid. Name single-call latency, batch
  throughput, instrumented component cost and compile/cache procedures
  distinctly; method IDs are meaningful producer-owned identifiers.
- `provenance`: boolean `has_provenance` and `qualified`; `host` and
  `measured_at` (UTC timestamp), each nullable with `provenance.unknowns`
  reasons. Qualified evidence requires `has_provenance: true`.
- `validation`: `status` (`accepted`, `unreviewed`, `rejected`) and a non-empty
  `reason`. Accepted records must be qualified; these are producer declarations,
  never an acceptance decision inferred by Pulse.
- `evidence`: repo-relative `path` and optional string/null `fragment`, resolved
  at the captured project commit. Absolute paths, URLs and traversal are refused.

Memory metrics are explicitly `host_peak_rss`, `device_peak_allocated`,
`device_peak_reserved`, or `device_total`; the last is device capacity, **not**
measured application VRAM. Additional memory meanings require an explicit
contract extension. Component timings remain `axis: breakdown`, never runtime.

### Explicit selections and coverage

A selection represents one declared measurement slot, with `id`, `setup_id`,
`axis`, `metric`, `unit`, `method_id`, full `identity`, `host`, `status`,
`record_id`, and a non-empty `reason`. Unknown host uses `unknowns.host`.

For `accepted` or `unreviewed`, `record_id` must resolve, and the setup, axis,
metric, unit, method ID, complete identity (including software revisions), host
and validation status must match the named record. Duplicate slots are refused.
The producer chooses references; Pulse never selects a latest/fastest row.
Other states (`not_measured`, `failed`, `unusable`, `inapplicable`) require
`record_id: null`. Diagnostic artifacts can remain linked from findings;
a failed run is never presented as a zero-cost successful measurement.

`coverage.expected.cells` equals the selection count. `coverage.observed`
contains accurate `setups`, `records`, and `selected` counts. This distinguishes
a declared missing GPU cell from an undeclared cell. The common `excluded`
list retains excluded evidence and reasons. An empty catalogue is no evidence,
not a scientific pass.

### Hazards and recommendations

Both have `id`, `title`, `description`, non-empty `evidence` (objects with safe
`path` and optional `fragment`), and `applies_to`:

- non-empty `setup_ids` referencing exact setups;
- non-empty `library_versions` naming applicable measured versions;
- `constraints` object, plus a non-empty `limitations` string.

Hazards have `status: open | resolved | unknown`. Recommendations additionally
have non-empty `record_ids` and `validation` as above. Supporting records must
belong to the applicable setups and library versions; an accepted recommendation
requires accepted supporting records. Constraints and scientific claims remain
producer-owned: the reader checks structure and reference integrity, not whether
a recommended solver is correct. Consumers must inspect the cited records'
hardware/method and applicability, and must not extrapolate to a different setup
or interpret a per-likelihood measurement as a total-fit prediction.

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


### Browsing measurement availability

The setup browser lists runtime, breakdown, compilation and memory availability
per model/instrument, then selects one exact evidence run. Runtime evidence is
the deterministic default when available; exact run links open a populated axis
without substituting a different setup. Selecting a device narrows recorded runs,
and a compatible filter persists when changing runs. Counts describe availability,
not scientific comparability or acceptance.

Optional shard `axes` and `axis_devices` metadata supplies the overview. Older
captures fall back to their inline or verified loaded records; device-wide lists
are never treated as an axis/device cross-product. Missing axis summaries remain
explicit and their runs can still be opened. No recorded memory is displayed as
missing evidence, never estimated from another axis.

Optional unbound-finding `discovery.models` entries identify related model
findings; `discovery.shared` identifies shared component/method findings. Both
remain applicability-unverified and separate from exact setup/version bindings.
Findings without discovery metadata remain accessible as uncategorized evidence.
Original evidence links and shard fetches retain the captured commit; local
checkout captures cannot silently fetch remote details.

The browser regression fixture `tests/fixtures/browser_measurements.json` is a
seven-setup subset captured from autolens_profiling commit
`16471e3f6cb7acc1ebe8392af3934821bc254dea`. Its embedded shard bytes and hashes
are unchanged; the catalogue is scoped to those setups for hermetic browser tests.
It includes MGE/rectangular HST runs without reference candidates and without
memory measurements, so empty-memory and useful-runtime behavior are both tested.

Likelihood navigation labels known implementations explicitly as (JAX) or (Numba).
Unspecified implementation variants are omitted from the menu without relabelling
their evidence; existing direct links remain supported. Menu priority is Delaunay,
Rectangular, MGE, KNN, MGE Mass, Sersic, then other families alphabetically.

Sersic retains one plain menu entry when only unclassified latent tools exist;
this does not assign a backend. Known Sersic variants replace that fallback.

## Decision History

`decisions.yaml` indexes human-authored campaign summaries; `decisions/README.md`
defines capture, ownership, record format and supersession. The flat list follows
Results in HTML and Markdown. Both boards can link to one canonical record.
The reader validates IDs, dates, GitHub destinations and owned record metadata;
it never makes a scientific decision. Remote record existence is checked when
publishing the cross-dashboard link, not by offline rendering.
