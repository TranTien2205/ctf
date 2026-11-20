# Investigation report shape

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Per question: answer, evidence, confidence,
corroboration. The sweep produces the sections;
the main thread writes the narrative.

## Exit

Step done -> next phase module or merge rules.
