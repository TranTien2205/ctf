# Signature: filesystem magic

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

ext 0x53EF at 0x438, NTFS 'NTFS    ' at 3, FAT
0x55AA at 510 - the fs type names the parse tool.

## Pivot

Artifact identified -> its route-* module and depth skill.
