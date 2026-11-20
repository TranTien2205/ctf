# Defense cell: rate-limit vs multi-turn

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

Whether `multi-turn` defeats `rate-limit`.

## Coverage

What this defense actually inspects (raw input, normalized input,
generated output, tool calls) and where this evasion family's
surface sits relative to the inspection.

## Result shape

Which evasions this defense catches by construction and which it
misses by design - the cell is a coverage map, not a guarantee.

## Pivot

Cell read -> `../llm-attacks.md` for the filter-layer model or
`trap-filter-layer.md` for the boundary analysis.
