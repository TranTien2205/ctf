# IOC flow to report

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

IOCs found during the sweep (IPs, hashes, names)
merge into one IOC set on the main thread - the
report's appendix.

## Exit

Step done -> next phase module or merge rules.
