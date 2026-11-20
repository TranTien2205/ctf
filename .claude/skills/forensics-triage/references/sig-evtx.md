# Signature: EVTX

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

ElfFile\x00 - the chunked event log; tools/forensics
evtx tooling or python-evtx.

## Pivot

Artifact identified -> its route-* module and depth skill.
