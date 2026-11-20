# Question: which protocol matters

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

For a pcap: protocol hierarchy (tshark -q io,phs)
before any packet reading - the answer usually sits
in one protocol.

## Pivot

Artifact identified -> its route-* module and depth skill.
