# Sherlock question shapes

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

HTB Sherlocks phrase questions operationally
('what was the C2 IP') - map phrasing to family
before slicing, not during.

## Exit

Step done -> next phase module or merge rules.
