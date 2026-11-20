# Learning loop

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## field-notes.md entries

Record what the bundle actually showed: which channel, which tap caught it,
which trap cost a pass, and what the falsifier evidence looked like on a
clean bundle. Proposed notes promote to confirmed only through a solve —
`security-skill-evaluation` carries the bar.

## Feeding back

A channel shape this corpus missed belongs in a new `chan-*` module plus a
`corpus-index` regeneration — not in prose memory. The index is generated
from the files on disk, so the file is the fact.
