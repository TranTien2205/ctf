# tshark

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

pcap dissection: -q io,phs hierarchy, -Y filters,
-T fields extraction, --export-objects. The whole
pcap workflow.

## Pivot

Artifact identified -> its route-* module and depth skill.
