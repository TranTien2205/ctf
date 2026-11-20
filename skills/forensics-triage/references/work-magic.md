# Magic over extension

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

Extensions lie constantly in forensics handouts - the
first four bytes decide: file, xxd | head, or
tools/file_type.py.

## Pivot

Artifact identified -> its route-* module and depth skill.
