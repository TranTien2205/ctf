# Workflow: The TSV shape for pandas

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Header line first, `\t` separated, `// "-"` for absent fields - dtype=object read; to_datetime utc for eventTime; sort on ts. The pipeline in the SKILL's day-zero block.

## Pivot

Workflow covered -> `scen-*` for the bundle shape.
