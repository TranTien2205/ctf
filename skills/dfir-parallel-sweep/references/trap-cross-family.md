# Trap: agents crossing families

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

An agent citing outside its family means the
slice was wrong - fix the slice at merge, never
accept the out-of-family claim.