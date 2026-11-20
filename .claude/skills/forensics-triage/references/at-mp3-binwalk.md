# Artifact cell: mp3 / binwalk

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

Whether `binwalk` applies to the `mp3` artifact.

## Fit

First-tool, useful, or wrong-format - the artifact's
structure against what the tool reads. First-tool pairings
carry the exact invocation; wrong-format pairings state the
refusal so the tool is never wasted.
