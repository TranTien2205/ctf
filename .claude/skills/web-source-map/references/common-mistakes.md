# Common mistakes — the ways the map pass goes wrong

## Mining only `main`

The most common miss: the entry page loads `main.js` + a dozen chunks,
and only `main` is mined. The interesting endpoint lives in a page
chunk or a lazy-loaded module. Enumerate every script, mine every
bundle, fetch the manifest for the lazy routes.

## Reading the whole bundle into context

A 5MB minified bundle read whole drowns context. Grep for the specific
token (endpoint, param, secret, flag shape) or let `bundle_miner`
inventory it. The only file read whole is a recovered `sourcesContent`
source.

## Claiming "recovered the source" on a string grep

A minified bundle with no map yields *strings*, not source — you found
an endpoint string, not the code. Only a `sourcesContent` recovery is
the real source. Do not present grepped strings as having "read the
application".

## Treating a string as an endpoint

`/api/admin` in the bundle is a *claim* — it may be a dead client
route, a renamed path, or a react-router path that never hits the
server. Verify the endpoint responds before treating it as a target.

## Treating a secret candidate as a leak

A high-entropy string is a *candidate*. `pk_live_` is publishable; a
dead token is not a finding. Verify the secret *works* — it
authenticates, it decodes — before presenting it as a leaked
credential.

## Confusing a 200 with a map

A `.map` request returning `200 text/html` is the SPA's catch-all route
serving the index page, not a source map. Check the content type and
the `{"version":3` first bytes.

## Ignoring the untrusted-source rule

The bundle and map are attacker-controlled. A `sources` path that
escapes `--out` is a traversal, not a recovery — `bundle_miner`
rejects it. Read recovered source; do not execute it.

## Stopping at recon

The map produces leads, not flags — the endpoint it named still needs
its own bug class, the secret still needs verification. Stopping after
the map pass because "I found endpoints" leaves the finding unmade.
Route each lead to its class.

## Re-mining a dead bundle

A bundle that produced nothing does not change on a second pass — the
strings are fixed. Record the negative and move to a different recon
layer, not a repeat of the same mine.
