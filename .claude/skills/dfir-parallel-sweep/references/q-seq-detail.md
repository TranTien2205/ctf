# Question detail: sequence

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

'Before/after/during' questions are timeline-
fusion products - the merge builds them, agents
supply per-family anchors.

## Exit

Step done -> next phase module or merge rules.
