# Negative: single-artifact task

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

One artifact, one question - open it directly;
a sweep's overhead exceeds one read.