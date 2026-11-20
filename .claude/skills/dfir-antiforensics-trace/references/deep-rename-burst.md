# Deep: The SDelete rename burst decoded

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

26 pairs of `0x1000` (rename old) + `0x2000` (rename new) journal records on ONE FileReferenceNumber, names marching AAA.AAA -> ZZZ.ZZZ — Microsoft's documented behaviour 'each time replacing each character of the file's name with a successive alphabetic character'. Counting pairs on the FRN is the detection; the count (26) is the fingerprint.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
