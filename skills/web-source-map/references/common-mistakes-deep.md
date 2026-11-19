# Common mistakes (deep) — the failure shapes in detail

## The `main`-only mine

The most common miss: the entry page loads `main` + a dozen chunks, and
only `main` is mined. The interesting endpoint lives in a page chunk or
a lazy module. **Fix**: enumerate every script AND the manifest's lazy
routes before deciding the bundle is thin.

## The whole-bundle read

A 5MB minified bundle read into context drowns it and surfaces nothing —
the strings are there but context cannot hold the file. **Fix**: grep
for the specific token, or `bundle_miner` inventories it. Read only
recovered `sourcesContent` whole.

## "Recovered the source" on a string grep

A minified bundle with no map yields *literals*, not the program — you
found `"/api/admin"`, not the code that calls it. **Fix**: only a
`sourcesContent` recovery is "the source"; a grep is "the strings". Do
not present a grep as having read the app.

## The endpoint-claim claim

`/api/admin` in the bundle is a *claim* — it may be a dead client route,
a renamed path, or a react-router path that never reaches the server.
**Fix**: verify it responds live; a 404 means the string outlived the
route.

## The secret-leak claim

A high-entropy string or `apiKey` is a *candidate*. `pk_live_` is
publishable; a dead token is not a finding. **Fix**: verify it
authenticates/decodes before presenting it as a leaked credential.

## The 200-is-a-map trap

A `.map` request returning `200 text/html` is the SPA catch-all serving
the index, not a map. **Fix**: check `content_type` and the
`{"version":3` first bytes, not the status.

## The vendor-bundle read

Mining `chunk-vendors`/`vendor.js` — react/lodash/axios — surfaces
dependency internals, not app logic. **Fix**: skip the vendor bundle;
the app logic is `main`/`app`/page chunks.

## The untrusted-source execution

A recovered `sourcesContent` is attacker-controlled — a `sources` path
is a traversal, a recovered "source" can be planted. **Fix**: read it;
never execute it; `bundle_miner` rejects a traversal.

## Stopping at recon

The map produces leads, not flags — the endpoint still needs its class,
the secret still needs verifying. **Fix**: route every lead; the map's
job is to name the target, the class's job is to close it.

## Re-mining a dead bundle

A mined bundle's strings are fixed — a second pass produces the same
nothing. **Fix**: record the negative; move to the routed class or a
different recon layer.

## The catalogue-as-verified claim

Presenting a published map-mining shape as "what worked here" — this is
a catalogue class, no local verified solve. **Fix**: honest evidence
level; record a real solve to promote.
