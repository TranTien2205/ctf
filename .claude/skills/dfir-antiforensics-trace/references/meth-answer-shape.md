# Method: Answer shapes this class emits

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

'1102 at T by user U cleared Security' / 'gap (a,b) = N records deleted between T0..T1' / 'Sysmon 2 shows Previous=X planted=Y on path P' / 'quarantine ResourceData carved to H'. Each names the artifact and the field — the class never emits a bare verdict.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
