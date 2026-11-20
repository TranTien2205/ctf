# Merge order

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Answers with verbatim evidence first, conflicts
resolved by timestamp correlation, gaps re-sliced
to the family that can fill them.