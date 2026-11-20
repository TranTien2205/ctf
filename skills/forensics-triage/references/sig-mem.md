# Signature: memory image

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

No reliable magic - size, entropy, and strings
density distinguish a memdump from a disk image.

## Pivot

Artifact identified -> its route-* module and depth skill.
