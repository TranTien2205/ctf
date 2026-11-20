# Scenario: Evidence a shredder ran

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

$J 26-rename burst on one FileReferenceNumber (AAA.AAA shape), Sysmon 28 FileBlockShredding naming the tool, SDelete EulaAccepted key, EFSTMPWP at volume root, tiny equal-sized MFT-fill records. Any one is the tamper record; the file itself is not coming back — pivot to name/times/quarantine copies.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
