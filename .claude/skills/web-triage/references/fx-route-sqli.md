# Reach cell: route via sqli

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

Can `sqli` reach a flag located in `route`?

## Read

Reach means: the class's proven primitive (query read, file read,
exec, identity change, viewer action) can touch this flag location
without an unproven second hop. Answer direct, one-hop, or
unreachable - with the hop it would need.

## Route

Direct or one-hop keeps the class on the candidate list for this
challenge. Unreachable demotes it regardless of signal strength -
the flag pulls the route, and a class that cannot reach the flag
is not this challenge's bug.
