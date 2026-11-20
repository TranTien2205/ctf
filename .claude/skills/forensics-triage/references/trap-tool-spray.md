# Trap: every stego tool on everything

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

zsteg on a jpg does nothing (png/bmp only);
steghide on png fails (jpg/wav). Match the
tool to the format.

## Pivot

Artifact identified -> its route-* module and depth skill.
