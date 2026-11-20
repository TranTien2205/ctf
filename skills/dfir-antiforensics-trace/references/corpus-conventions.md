# Corpus conventions

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` first.

## Conventions

- Every module opens with a pointer back to the class contract.
- the `*-route` companion cards name the question and constraint a module feeds.
- the `*-deep` companion cards carry format internals and failure modes.
- `mx-*` cells are the recovery table expanded one column each.
- The index (`corpus-index.md`) is generated from files on disk —
  regenerate it whenever files are added, never hand-edit the list.

## Discipline

Artifact + field + verbatim row in every answer; negatives recorded with
the probe that produced them; three shapes per family then pivot.
