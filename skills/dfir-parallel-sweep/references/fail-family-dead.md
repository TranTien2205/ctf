# A dead family

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

An artifact family absent or empty: its question
slice re-routes at merge time; the report records
the absence, not a guess.