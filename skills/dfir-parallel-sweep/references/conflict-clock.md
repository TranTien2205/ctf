# Timestamp conflicts

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Clock skew between artifacts: the merge orders
by the most reliable source (evtx SystemTime)
and notes skew estimates.

## Exit

Step done -> next phase module or merge rules.
