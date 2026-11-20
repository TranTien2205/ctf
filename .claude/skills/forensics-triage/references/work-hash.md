# Hash first

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

md5sum/sha256sum the artifact before touching it - the
writeup needs the hash and some flag answers ARE the
hash of the right file.

## Pivot

Artifact identified -> its route-* module and depth skill.
