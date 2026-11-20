# Artifact priority within family

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Each family ranks its own artifacts (Security
> other evtx for auth; $MFT > .pf for fs
timeline) - the brief states the order.

## Exit

Step done -> next phase module or merge rules.
