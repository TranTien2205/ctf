# Question detail: who

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

Logon IDs, session types, source IPs - the auth-
family artifacts; answer is actor + evidence,
never 'the attacker probably'.

## Exit

Step done -> next phase module or merge rules.
