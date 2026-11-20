# Reporting gaps

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

A question no family answers is reported as
'not in bundle' with the artifacts checked -
a negative result, not a blank.

## Exit

Step done -> next phase module or merge rules.
