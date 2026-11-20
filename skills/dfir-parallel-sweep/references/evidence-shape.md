# DFIR evidence shape

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Artifact path + locator (offset/event id/line/
packet number) + verbatim bytes - weaker shapes
do not merge.