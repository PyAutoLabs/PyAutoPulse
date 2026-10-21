# Decision records

Decision History is a flat, newest-first list below the dashboard's Results.
It is not divided by repository, dataset or likelihood. Entries open readable
GitHub Markdown pages in new tabs.

## Capture a decision

Say **"record this decision"**, or explicitly flag a key campaign decision,
in the ongoing campaign conversation. Follow CHECKIN.md's decision capture
procedure. A dedicated skill is not required: the check-in instructions are
the entry point for both natural-language forms.

Write one canonical `decisions/<id>.md` in the organ leading the campaign.
Use the template below; do not index the template or an undecided draft.
Add the same id, title, date and canonical URL to `decisions.yaml` in each
relevant dashboard. Cross-dashboard entries link to the same page; never copy
the decision prose. The date is the date the human made the decision, not the
board refresh date. Quote it in YAML. IDs are stable lowercase kebab-case.

The index has exactly one `decisions` list; each entry has `id`, `title`,
`date` (YYYY-MM-DD string), and `url` pointing to
`https://github.com/PyAutoLabs/<owning-organ>/blob/main/decisions/<id>.md`.
The owning organ is PyAutoPulse or PyAutoInsight. Its local record must exist
and its heading and Date line must match the index. Publish the canonical
record before adding a link from the other dashboard, then verify that link.
Evidence references within the record should pin commits or immutable results.

Keep old decisions visible. A changed choice gets a new dated record with a
"Supersedes" link; add a "Superseded by" link to the old page without rewriting
its original reasoning. Clarifying factual corrections are dated annotations.
An agent's proposed interpretation is not a human decision. Cortex/project
ledgers remain authoritative for scientific facts and human conclusions;
these pages summarize and cite them. Recording does not implement the choice,
submit compute, change defaults or certify scientific acceptance.

## Record template (not a published decision)

```markdown
# <Decision title>

Date: YYYY-MM-DD
Decision maker: <human>
Decision source: <human statement and durable source link, or dated conversation quotation>

## Campaign
<Goal, motivation and scope across repositories/datasets.>

## Evidence
<High-level findings with pinned links; hardware, precision, model, cold/warm
start and timing definitions where relevant. Include uncertainty and failures.>

## Options considered
<Alternatives and consequential tradeoffs.>

## Decision
<The human's actual choice, its scope and any exceptions.>

## Implications
<Effects on likelihoods, SLaM/inference defaults, compatibility and follow-up
work. Distinguish decided direction from implementation already shipped.>

## Revisit conditions
<Remaining uncertainty and what new evidence would change the choice.>

## History
<Supersedes/superseded-by links when applicable.>
```

## Designation decisions (`kind: designation`)

A designation is the human's choice of the optimal and secondary setups for one
likelihood, regime and hardware class. It is a decision like any other (one
canonical record, one index row), with extra fields on its `decisions.yaml`
entry so `profiling-summary@3` records can cite it:

| Field | Meaning |
|---|---|
| `kind` | `designation`. Without it, the designation fields below are refused. |
| `likelihood` | `<dataset_type>/<variant>`, e.g. `imaging/delaunay`; `dataset_type` is one of the ten in REFERENCE.md. |
| `regime` | The named size bin the rule branches on, e.g. `standard` or `n_vis_1e5_1e7`. |
| `hardware_class` | `cpu_many_core`, `gpu_a100` or `laptop`. |
| `optimal` | One canonical `setup_id`, `<backend>_<device>_<operator>_<precision>[_<transformer>]`. |
| `secondary` | A list of canonical `setup_id`s (may be empty), distinct from `optimal`. |
| `evidence` | A non-empty list of the record ids the decision rests on. |
| `rule` | One sentence, in terms of dataset properties, that an agent can apply from data alone. |
| `supersedes` | The id of the designation this one replaces, or `null`. |

A record with `class: optimal` must carry a `decision_id`, and `pyauto-pulse
check` resolves it against this index. Pulse never writes a designation from
timings: the producer declares the class, the human makes the decision, and
the record cites it. Index entry template (not a published decision):

```yaml
- id: <likelihood>-<regime>-<hardware-class>
  title: <Decision title>
  date: 'YYYY-MM-DD'
  url: https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/<id>.md
  kind: designation
  likelihood: <dataset_type>/<variant>
  regime: <regime>
  hardware_class: <cpu_many_core | gpu_a100 | laptop>
  optimal: <setup_id>
  secondary: [<setup_id>, ...]
  evidence: [<record id>, ...]
  rule: <one sentence in dataset-property terms>
  supersedes: null
```

The canonical `decisions/<id>.md` record uses the template above; its
Decision section states the optimal and secondary setups and the rule, and its
Evidence section links the cited records at pinned commits.
