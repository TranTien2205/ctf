# Deep: Tamper protection ordering

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

5013 (blocked) means the attempt failed and the settings stand; 5001/5010/5012 mean a disable actually landed. If both exist, ORDER them — a blocked-then-disabled sequence means the attacker worked around tamper protection (often via a kernel/driver route or a trusted path).

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
