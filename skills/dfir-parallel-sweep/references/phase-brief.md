# Phase: briefs

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Each brief carries the family's artifact paths, the
question list slice for that family, the return
contract, and the read-only rule.