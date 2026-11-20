# Route cell: syslog -> forensics-pcap-carve

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

Whether `syslog` routes to `forensics-pcap-carve`.

## Read

Strong-owner, partial, or rules-out - the artifact's
dominant question against the route's scope. Partial
routes carry the condition that flips them.
