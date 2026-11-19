# Anti-patterns — what this skill must not do

## Do not claim a bundle string is a finding

`/api/admin` in the bundle is a lead, not a discovery — verify it
responds live. A string is a claim the client makes; the server's
response is the fact.

## Do not claim a secret candidate is a leak

A high-entropy string or `apiKey` is a candidate — verify it
authenticates. `pk_live_` is publishable; a dead token is not a
finding.

## Do not claim "recovered the source" on a grep

String mining yields literals; only a `sourcesContent` recovery is the
real commented source. A grep is not "reading the application".

## Do not read the whole minified bundle into context

Megabytes of minified code drowns context. Grep for the token or let
`bundle_miner` inventory it. Read only recovered `sourcesContent`
whole.

## Do not treat the map as the exploit

The map is recon — it names endpoints, secrets, routes; the routed
class closes the finding. Stopping at "I found endpoints" leaves the
bug unmade.

## Do not execute recovered source

The map is attacker-controlled — a `sources` path can be a traversal,
a recovered "source" can be planted. Read it; never run it.

## Do not re-mine a dead bundle

A mined bundle's strings are fixed — a second pass produces the same
nothing. Record the negative; move to the routed class or a different
recon layer.

## Do not present catalogue as verified

This class has no local verified solve — the shapes are standard
published knowledge, not "what worked here".
