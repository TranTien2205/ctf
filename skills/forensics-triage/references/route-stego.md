# Route: stego family

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

Image/audio/video carrying hidden data ->
forensics-stego; media metadata answers sit in
osint-media-metadata only when the question is
about the metadata itself.

## Pivot

Artifact identified -> its route-* module and depth skill.
