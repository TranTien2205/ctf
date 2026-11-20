# Artifact: container/archive

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

zip/tar/7z with nested or passworded contents -
compression artifacts; john/zip2john for the password
layer when present.

## Pivot

Artifact identified -> its route-* module and depth skill.
