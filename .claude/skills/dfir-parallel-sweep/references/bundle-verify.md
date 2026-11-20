# Verifying the bundle

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Artifact inventory vs the expected set - a
missing family discovered at merge time wastes
an agent slot; verify upfront.

## Exit

Step done -> next phase module or merge rules.
