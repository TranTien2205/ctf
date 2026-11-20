# Intake pipeline

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

hash -> identify -> route -> analyze. Hash the artifact
first (evidence discipline even in CTF), identify by magic
not extension, route to exactly one depth skill.

## Pivot

Artifact identified -> its route-* module and depth skill.
