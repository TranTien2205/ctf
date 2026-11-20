# Cross-family corroboration

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

A claim from one family confirmed by another
(prefetch run + Sysmon 1) - corroborated answers
outrank single-source ones.

## Exit

Step done -> next phase module or merge rules.
