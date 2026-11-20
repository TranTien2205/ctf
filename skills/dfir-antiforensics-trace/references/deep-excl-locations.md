# Deep: Every place an exclusion can live

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions\{Paths,Extensions,Processes}` (local), `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Exclusions\` (policy/GPO), plus 5007 New value strings naming the changed value, plus command-line evidence. A policy-path exclusion suggests domain push, a local-path one suggests console/API write — the path answers 'who'.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
