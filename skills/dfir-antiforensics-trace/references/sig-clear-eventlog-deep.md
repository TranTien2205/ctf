# Deep: sig-clear-eventlog

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base signature: `sig-clear-eventlog.md`. The command's own execution record is the first half; the artifact change it produces is the second — reporting needs both halves.

## Attribution chain

CommandLine/4104 record (who + when) -> artifact change (what it did) -> the cleared/hidden content's recovery column (what survived anyway).

## Evidence rule

The signature alone is not tampering — administrators run these legitimately. The pair (signature + artifact effect + window context) is the finding.
