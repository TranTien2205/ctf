# file / file_type.py

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

The intake tool: magic -> type. tools/file_type.py
is the stdlib fallback with the same answer.

## Pivot

Artifact identified -> its route-* module and depth skill.
