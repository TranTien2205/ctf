# Trap: strings-only analysis

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

strings finds plaintext flags; it misses
everything structured, encoded, or deleted -
it is step one, never the whole method.

## Pivot

Artifact identified -> its route-* module and depth skill.
