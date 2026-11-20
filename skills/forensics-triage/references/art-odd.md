# Artifact: unknown blob

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

No magic match - entropy measurement (binwalk -E),
strings -e l, and the structure hunt. Sometimes it is
a raw filesystem without partition table or a carved
fragment.

## Pivot

Artifact identified -> its route-* module and depth skill.
