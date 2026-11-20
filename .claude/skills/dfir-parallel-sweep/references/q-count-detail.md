# Question detail: counts

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

How many times X - counting belongs to the
artifact that records X, with the query stated.

## Exit

Step done -> next phase module or merge rules.
