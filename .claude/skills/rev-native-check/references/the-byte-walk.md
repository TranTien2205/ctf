# The byte walk — the per-character loop


A compare loop: for each byte, transform and compare — the loop's
body is the check; the loop bound is the length.

## The read

The loop body's compare operand is the per-position expected value —
a table index or a transformed constant per i.
