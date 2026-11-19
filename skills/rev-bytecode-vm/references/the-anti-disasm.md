# Anti-disassembly — when bytes aren't code

## Data-as-code

Bytes that look like ops but are data (an embedded table in the
program stream) — pc never lands there; skip.

## Overlapping instructions

A jump landing mid-instruction — the alternate decode is a trap;
follow real targets.

## The rule

The EXECUTED decode is truth — byte-order decode lies when jumps
overlap.
