# Question detail: when

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Timestamps must name their artifact and field
(EventTimeCreated, $MFT SI vs FN, prefetch last-
run) - one timestamp, one source.

## Exit

Step done -> next phase module or merge rules.
