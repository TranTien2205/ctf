# Slicing the question list

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Assign each question to the ONE family most likely
to hold its answer; cross-family questions get a
primary family plus a corroborating note.