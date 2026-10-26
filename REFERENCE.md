# PyAutoPulse — reference

The [campaign control room](CHECKIN.md) provides one editable check-in prompt,
active campaigns and Pulse-owned tasks above the detailed profiling evidence.
`campaigns.yaml` is the scheduling ledger; `migration.yaml` records original Mind
prompts and their source commit. Board refreshes never change task status or stamp
a check-in. Run `bin/pyauto-pulse board --offline` after ledger edits.

The registry schema, the `profiling-summary` contracts as this organ reads
them (v1 historical, v2 the live registry pin, v3 the lifecycle catalogue now
supported), the `walltime-validation` v1 evidence axis, and the formats of the receipts, snapshots, board markers and cockpit feed.
Prose boundaries live in [AGENTS.md](AGENTS.md); the design is
[profiling_inference_organs.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/research/profiling_inference_organs.md).

## Registry (`registry.yaml`, `schema: 1`)

One row per instance under `instances:`. Unknown fields are refused.

| Field | Required | Meaning |
|---|---|---|
| `instance` | yes | Stable key within the organ, `^[a-z][a-z0-9_-]*$`, unique. |
| `repo` | yes | A PyAutoMind body-map identity (`repos.yaml` key). `path` and `github` are read from the body map at load time and **may not** be written in the row. |
| `summary_path` | yes | Repository-relative path of the producer's summary (no `/`-prefix, `..`, URL). |
| `supported_schema` | yes | `<schema>@<integer version>` the reader expects and implements: `profiling-summary@1`, `@2`, `@3` or `walltime-validation@1`. Any other pin is refused. |
| `dashboard_url` | yes | The project's own human-facing page (`https://`). |
| `library_refs` | no | Body-map identities the project exercises (each must be in the body map). |
| `cortex_project` | no | An existing Cortex key, or `null`. |

Further rules: the same `(repo, summary_path)` may be registered once (disjoint
scopes; no inflated coverage). Every ingest reads branch `main`. A project that
publishes wall-time validation registers it as a second instance row with its
own `summary_path` and `supported_schema: walltime-validation@1`.

Body map resolution order: `--mind PATH` (must hold `repos.yaml`, never a
silent fall-through), `$PYAUTO_MIND`, `$PYAUTO_ROOT/organs/PyAutoMind`,
`$PYAUTO_ROOT/PyAutoMind`, then beside this organ (grouped `organs/` or flat
task-bundle layout). No body map → an error, never a guess.

## `profiling-summary` v1, as read here (historical)

The producer documents the contract
([autolens_profiling `dashboard/README.md`](https://github.com/PyAutoLabs/autolens_profiling/blob/main/dashboard/README.md));
this is what `pulse/summary.py` enforces. Additive fields are ignored. No live
registry row pins v1 today; saved v1 snapshots and fixtures still validate.

**Support.** `(schema, version)` must be one this reader implements
(`profiling-summary` 1, 2 or 3, `walltime-validation` 1) *and* match the
registry row's `supported_schema`; otherwise the outcome is **unsupported** and
nothing else is validated. The envelope, record and comparison rules below are
the v1 shape; v2 and v3 reuse the envelope.

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

V2 is the live registry pin for both instances (`lens`, `fit`). Registry entries
pin an exact version; supporting a newer version never silently upgrades a row
or reinterprets a saved snapshot of an older one. The full
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

## `profiling-summary` v3: lifecycle catalogue

V3 is v2's envelope with every record declaring where it sits in the
likelihood lifecycle. The [synthetic fixture](tests/fixtures/setup_summary_v3.json)
is an executable producer example; validation is stdlib-only in
`pulse/catalogue.py`. The producer declares `class` and `status`; Pulse checks
that the declarations are consistent and renders them. It infers no optimal
setup, selects no fastest row and computes no ratio.

**Envelope.** The common v1 envelope (as v2), `comparisons: []`, plus:

- `records`: list (empty is valid; an empty catalogue is no evidence).
- `planned_cells` (optional list): the cells the producer intends to measure,
  each with the key fields below and `class`. Duplicate cells are refused.
- `archive_record_count`: non-negative integer. Archived records are moved out
  of `records[]` by the producer and only counted here.
- `hazards`, `recommendations` (optional): the v2 shape; `applies_to.setup_ids`
  name canonical v3 `setup_id`s present in `records`.
- `coverage.expected.cells` equals the `planned_cells` count;
  `coverage.observed.records` equals the record count, and `current` /
  `superseded`, when present, match the declared statuses.

**Vocabulary** (the validator's enumerations):

| Field | Values |
|---|---|
| `likelihood.dataset_type` | `imaging`, `interferometer`, `datacube`, `point_source_image`, `point_source_source`, `multi_galaxy`, `group`, `cluster`, `multi_dataset`, `weak` |
| `likelihood.variant` | non-empty string, e.g. `delaunay`, `mge`, `source_plane` |
| `setup.backend` | `numba`, `jax` |
| `setup.device` | `cpu`, `gpu` |
| `setup.operator` | `dense`, `sparse`, `na` |
| `setup.precision` | `fp64`, `mixed` (mixed is expected to be `class: experimental`) |
| `setup.transformer` | `dft`, `nufft`, `wtilde`, `streaming`, `na` |
| `setup.threads` | positive integer or `null` |
| `setup_id` | `<backend>_<device>_<operator>_<precision>`, plus `_<transformer>` when the transformer is not `na`, e.g. `jax_gpu_sparse_fp64_wtilde` |
| `host_class` | `hpc_ral_cpu`, `hpc_a100`, `local_laptop`, `local_gpu` (provenance, never identity) |
| `measurement` | `runtime`, `breakdown`, `gradient`, `compile`, `memory_host`, `memory_device`, `parity`, `walltime_validation` |
| `class` | `optimal`, `secondary`, `experimental` |
| `status` | `current`, `superseded`, `archived` |

**Records.** Each record has `id` (unique), `run_id`, `likelihood
{dataset_type, variant}`, `instrument`, `regime` (the named size bin, e.g.
`standard`), `setup {backend, device, operator, precision, transformer,
threads}` and the matching `setup_id`, `host_class`, `model_variant` (e.g.
`default`, `light_fixed`), `measurement`, `metric`, `unit`, `values`, `class`,
`status`, `superseded_by`, `day_zero`, `figures`, `decision_id`,
`release_pin`, `measured_at`, and v2's `identity`, `method`, `provenance`,
`validation` and `evidence` with the same rules.

- `unit` belongs to the measurement: seconds for the time measurements, a
  memory unit for `memory_host`/`memory_device`, `dimensionless` for `parity`.
- `values` is a non-empty object of finite, non-negative numbers that contains
  the headline `metric` (a breakdown carries its components beside its total).
  Missing cells are `planned_cells`, never zero-valued records.
- `superseded_by` is `null` unless `status: superseded`, when it names another
  record in the same document.
- `day_zero`, `release_pin`, `decision_id`: string or `null`. `measured_at`:
  ISO-8601 UTC.
- `figures`: list of `{kind, path, sha256}` with safe repo-relative paths and
  64-hex digests (may be empty).

**Rules.**

- Exactly one `current` record per key (`likelihood`, `instrument`,
  `setup_id`, `host_class`, `model_variant`, `measurement`). The producer
  chooses which one under the day-zero rule; a second `current` is refused.
- `class: optimal` requires a `decision_id`. `pyauto-pulse check` and ingest
  resolve every `decision_id` against this organ's `decisions.yaml`
  (the `designation` decisions below); an unresolved id makes the capture
  **invalid**.
- `host_class` `local_laptop` or `local_gpu` is never `current`; such rows may
  be kept as `superseded` provenance.
- An `archived` record inside `records[]` is refused.

**Resources and projected node throughput** (likelihood-lifecycle phase 2x,
autolens_profiling#463/#465). Two optional, additive record fields; no version
bump. Absent is valid. Present but malformed makes the capture **invalid**.

- `resources`: what one evaluation occupies. `cpus_per_eval` (positive integer
  or `null`), `peak_rss_gb` (finite positive GB or `null`) and `source` (string
  or `null`: `row`, the producer's backfill file, …) are required keys.
  `devices_per_eval` (non-negative integer or `null`), `peak_rss_basis`
  (e.g. `sacct_maxrss`, `job_maxrss`), `cpus_per_eval_basis`, `sacct_job` and
  `peak_rss_note` are optional strings. A `null` `cpus_per_eval` needs a
  `reason`; a `null` `peak_rss_gb` needs a `reason` or `peak_rss_reason`.
- `projected_node_throughput` (runtime records only): `basis: projected`
  (the only accepted value; a projection is never a measurement), `status`
  `projected` or `not_projected`, `per_call_s` (positive or `null`) with its
  `per_call_source`, the `resources` keys echoed, `parallel_efficiency`
  `{value in (0, 1], source[, kind]}` and `not_modelled` (a string or a list of
  strings). `projected` names exactly one host and a `per_call_s`;
  `not_projected` names no host and gives a `reason`.
- A host is `{host, host_class, workers, bound_by, limits, calls_per_s}`.
  `host_class` must equal the record's own: a per-call time is never projected
  onto another machine. `limits` maps `cores`, `memory` and (for a `gpu` setup
  only, and then required) `gpus` to positive integer worker caps; `bound_by`
  names the smallest and equals `workers`; `calls_per_s` is finite and positive.

Pulse checks shape and internal consistency only. It never recomputes a
projection, and the board shows projected values marked **projected** with
their η, its source and the bounding limit (see Board below). The reasoning behind the
numbers, as decision rules for the autolens_assistant, is the knowledge page
[Comparing CPU-parallel and GPU-batched setups](knowledge/cpu_parallel_vs_gpu_batched.md).

**Board.** Under **Profiling Timings**, a v3 instance renders a runtime-only
table: one row per `measurement: runtime` record. Filters: Class (All by
default, then Optimal, Secondary, Experimental), Dataset type, Model,
Instrument, Hardware class. Only `current` rows show until History is ticked,
which adds `superseded` rows; archived records appear only as a count. A green
tally (top right, above History) counts the current rows. Columns: Dataset type
| Model | Instrument | Regime | Setup | Hardware class | Model variant |
**Runtime s** | **Est. 12-core s** | Class | ›. Setup is the `setup_id`
without its precision token (`jax_gpu_sparse_fp64` → `jax_gpu_sparse`); a
non-fp64 precision is appended to the model variant (`default+mixed`).
Runtime s is the producer's vmap per-call time
`projected_node_throughput.per_call_s`; Est. 12-core s is the producer's
`estimated_12_core.value_s` (numba CPU records only, — elsewhere). Both are
rounded to 5 decimal places for display only, with the exact value in the
tooltip; Pulse computes neither. A Coverage panel lists optimal `planned_cells`
with no current record, and "Extra Information" links the knowledge page.
Research lookups read `class: optimal` + `status: current` unless asked
otherwise. The v2 eligibility heuristics never apply to a v3 catalogue.

**Detail pages.** Each row's › opens that record's detail page on the same
board (`?view=setup&instance=<instance>&record=<record id>`): its runtime values
(including `single_jit_median` / `single_jit_block`), the 12-core estimate,
the breakdown, compile, memory and parity records on the same key
(`likelihood`, `instrument`, `setup_id`, `host_class`, `model_variant`,
`regime`) and the same status, as bars within each panel, the producer's node
throughput projection marked **projected** with η, its source and bound, class,
status, decision, validation, limitations, configuration, evidence and figure
links at the captured commit, and the record's history (every runtime record on
the key). An id that is not in the captured catalogue shows a status line and no
substitute.

## `walltime-validation` v1: full-fit evidence axis

A second evidence axis, produced by autolens_inference and registered as its
own instance row. These are **full-fit** measurements: one sampler run per
record. A per-likelihood `runtime` record is never read as a total-fit
prediction, and a full-fit wall time is never read as a per-likelihood cost.
The [fixture](tests/fixtures/walltime_validation_v1.json) is an executable
example; validation is stdlib-only in `pulse/walltime.py`.

**Envelope** — required: `schema` (`walltime-validation`), `version` (1),
`project` (non-empty), `generated_at` (ISO-8601 UTC), `producer_revision`
(40-hex or `null`), `records`; optional `limitations` (non-empty strings).

**Records** — each with a unique `id` and one record per key (`likelihood
{dataset_type, variant}`, `instrument`, `setup_id`, `host_class`,
`model_variant`, `sampler`, `seed`); a duplicate key is refused. Fields:

- `wall_s`, `implied_ms_per_eval`, `predicted_ms_per_eval`,
  `ratio_measured_over_predicted`, `parallel_efficiency` (relative to the
  1-core row of the same key), `max_log_likelihood`: finite number or `null`.
- `likelihood_evals`, `cores`: non-negative integer or `null`; `seed`:
  non-negative integer.
- `reference_runtime_record_id` (the day-zero `runtime` record compared with),
  `release_pin`, `slurm_job_id`: string or `null`.
- `parity_status` ∈ `match | diverged | not_assessed`.

Additive optional fields (still `@1`; absent is valid, present they are
type-checked): the producer's join of the run to a profiling runtime record —
`implied_s_per_eval` and `profiling_per_call_s` (finite number or `null`);
`profiling_record_id` (the matched `profiling-summary@3` record id),
`profiling_unmatched_reason`, `profiling_per_call_source`, `profiling_status`
(string or `null`); `size_match` (boolean or `null`: whether the run's source
pixels equal the profiling record's size bin); `source_pixels`,
`profiling_source_pixels` (non-negative integer or `null`).

Every derived number is computed and declared by the producer. Pulse renders
the records under **Inference Timings** and computes nothing (see Board); the
instance has no qualification flag, so it raises no "unqualified" item.

## Ingest

1. `GET https://api.github.com/repos/<owner>/<repo>/commits/main` → one 40-hex SHA
   (stdlib `urllib`, 20 s timeout, `User-Agent`, `Authorization: Bearer $GH_TOKEN`
   on API calls only, when set).
2. `GET https://raw.githubusercontent.com/<owner>/<repo>/<sha>/<summary_path>`.
3. Validate; for a `profiling-summary@3` document resolve every `decision_id`
   against `decisions.yaml`; write the receipt; on `ok` also write the snapshot.

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

A `profiling-summary@3` receipt also carries `"lifecycle": {"current": N,
"superseded": N, "archived": N}` (the producer's declared counts); receipts of
other schemas keep the shape above.

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
- A v3 instance's status lines add **Lifecycle** (`N current · N superseded ·
  N archived`), and its census item carries the same counts. A
  `walltime-validation` instance renders as its own table.
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

## Knowledge pages

`knowledge/` holds reference pages written as decision rules that agents (the
autolens_assistant first) read: the reasoning behind how a number should be
compared, never a human decision. Decisions stay in `decisions/` with their
`decisions.yaml` index. A knowledge page cites the producer's evidence at pinned
commits and is linked from the board where its numbers appear.

## Decision History

`decisions.yaml` indexes human-authored campaign summaries; `decisions/README.md`
defines capture, ownership, record format and supersession. The flat list follows
Results in HTML and Markdown. Both boards can link to one canonical record.
The reader validates IDs, dates, GitHub destinations and owned record metadata;
it never makes a scientific decision. Remote record existence is checked when
publishing the cross-dashboard link, not by offline rendering.

### Designation decisions

An entry with `kind: designation` records the human's choice of setups for one
likelihood, regime and hardware class. Its extra fields are validated only when
the kind is set: `likelihood` (`<dataset_type>/<variant>`), `regime`,
`hardware_class` ∈ `cpu_many_core | gpu_a100 | laptop`, `optimal` (one
canonical `setup_id`), `secondary` (list of distinct canonical `setup_id`s),
`evidence` (non-empty list of record ids), `rule` (one sentence in
dataset-property terms) and `supersedes` (a decision id in the index, or
`null`). `profiling-summary@3` records with `class: optimal` cite these entries
in `decision_id`. The template is in [decisions/README.md](decisions/README.md);
no designation is recorded yet.
