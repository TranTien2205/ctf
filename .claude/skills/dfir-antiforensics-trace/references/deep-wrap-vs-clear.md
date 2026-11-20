# Deep: Wrapped vs cleared vs truncated

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Three different file states that all look 'short': wrapped keeps writing over oldest records (oldest>1, contiguous, big file); cleared resets to id 1 with a fresh small file (oldest=1, often an 1102 as first record); truncated lost bytes at the END (file smaller than its header's chunk count implies — carve flag). Each answers a different 'what happened'.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
