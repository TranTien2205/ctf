# Corpus index - web-race-condition

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Families present in this corpus, counted from disk. Open the
family's own index or the module whose name matches the
question - do not restate their content here.

| Prefix | Modules | Files |
|---|---|---|
| `README-*` | 1 | `README.md` |
| `case-*` | 2 | `case-studies-deep.md`, `case-studies.md` |
| `check-*` | 1 | `check-then-act-alphabet.md` |
| `checklist-*` | 1 | `checklist.md` |
| `class-*` | 1 | `class-boundary.md` |
| `common-*` | 4 | `common-mistakes-deep.md`, `common-mistakes.md`, `common-questions-deep.md`, `common-questions.md` |
| `database-*` | 1 | `database-isolation.md` |
| `delivery-*` | 1 | `delivery-mechanics.md` |
| `detection-*` | 5 | `detection-deep.md`, `detection-index.md`, `detection-matrix.md`, `detection-surface.md` (+1 more) |
| `edge-*` | 2 | `edge-cases-deep.md`, `edge-cases.md` |
| `evasion-*` | 1 | `evasion.md` |
| `evidence-*` | 2 | `evidence-rules-deep.md`, `evidence-rules.md` |
| `exploitation-*` | 4 | `exploitation-deep.md`, `exploitation-playbook.md`, `exploitation-shapes.md`, `exploitation.md` |
| `extended-*` | 1 | `extended-corpus.md` |
| `falsifiers-*` | 1 | `falsifiers.md` |
| `field-*` | 2 | `field-manual-deep.md`, `field-manual.md` |
| `glossary-*` | 1 | `glossary.md` |
| `interleave-*` | 1 | `interleave-patterns.md` |
| `interleaved-*` | 1 | `interleaved-writes.md` |
| `multi-*` | 1 | `multi-step-chains.md` |
| `neg-*` | 1 | `neg-shapes.md` |
| `negative-*` | 2 | `negative-results-deep.md`, `negative-results.md` |
| `payload-*` | 1 | `payload-variants.md` |
| `per-*` | 11 | `per-boundary.md`, `per-check-balance.md`, `per-check-deep.md`, `per-check-other.md` (+7 more) |
| `quick-*` | 1 | `quick-reference.md` |
| `race-*` | 1 | `race-catalogue.md` |
| `read-*` | 1 | `read-modify-write.md` |
| `real-*` | 1 | `real-world-cases.md` |
| `summary-*` | 1 | `summary.md` |
| `theory-*` | 2 | `theory-deep.md`, `theory.md` |
| `timing-*` | 1 | `timing-oracle.md` |
| `troubleshoot-*` | 2 | `troubleshoot-deep.md`, `troubleshoot.md` |
| `verified-*` | 1 | `verified-chains.md` |
| `whitebox-*` | 1 | `whitebox-hunt.md` |
| `window-*` | 1 | `window-catalogue.md` |
| `work-*` | 2 | `work-boundary2.md`, `work-closing-checklist.md` |
| `workflow-*` | 3 | `workflow-checklist.md`, `workflow-deep.md`, `workflow.md` |

## Reading order

1. `../SKILL.md` - first probe, falsifier, confirm shape, traps.
2. The `q-*`/`work-*` module matching the question asked.
3. The family module the question lands on.
4. A `*-route` card for the next family when the current one is spent.

## Discipline

Every module here is one piece of the corpus. A claim is a verbatim
response excerpt or artifact record passed through `tools/hooks.py` -
never a line from this index, which is routing information only.
