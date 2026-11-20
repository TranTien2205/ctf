# Timeline fusion

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Family answers with timestamps merge into one
sequence via timeline_merge - the sequence is a
main-thread product, not an agent's.