# Family x tool: registry / pcap-triage

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

The `registry` / `pcap-triage` pairing.

## Read

Strong-fit, partial, or excluded for this pairing - the cell
states the read plus the one check that settles a partial.
Excluded cells stay so the pairing is never re-derived.
