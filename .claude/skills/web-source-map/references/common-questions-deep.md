# Common questions (deep) — the extended FAQ

## Is this a vulnerability class?

No — it is a recon layer. It produces *leads* (endpoints, secrets,
routes, source) that route to the class that owns them. The finding is
the follow-on, not the map.

## The `.map` 404s — is the skill useless?

No — the common case. Production disables sourcemaps; string mining
yields endpoints/params/flags/secrets regardless. The map is a bonus.

## The bundle is huge — where do I look?

Grep for the specific token (endpoint, param, secret, `flag{`) or let
`bundle_miner` inventory it. Skip the vendor/runtime bundles — the app
logic is `main`/`app`/page chunks. Read only recovered
`sourcesContent` whole.

## "Recovered the source" — from strings?

No — string mining yields *literals*, not the program. Only a
`sourcesContent` recovery is the real commented source. Do not claim to
have "read the application" from a grep.

## A high-entropy string — a leak?

A *candidate*. `pk_live_` is publishable; a dead token is not a
finding. Verify it authenticates/decodes before presenting it as a
leaked credential.

## An endpoint string — a real route?

A *claim*. `/api/admin` may be a dead client route, a renamed path, or
a react-router path that never hits the server. Verify it responds
live.

## The map's `sources` path is `../../../etc/passwd` — a read?

A *traversal*, not a recovery — `bundle_miner` rejects and counts it.
The map is attacker-controlled; a hostile `sources` path does not write
outside `--out`.

## Only `main` was mined — did I finish?

No — the most common miss. The interesting endpoint lives in a page
chunk or a lazy module. Enumerate every script + the manifest's lazy
routes.

## A `200` on `.map` — the map exists?

Check the content type — a `200 text/html` is the SPA catch-all, not a
map. A real map is `application/json` starting `{"version":3`.

## The gated route (`PrivateRoute`) — protected?

Client-side only — the component and its endpoints are still shipped.
Probe the gated endpoint directly; the server may not enforce it.

## When is the route dead?

When every bundle is mined, the strings are opaque, no endpoint/secret/
route/flag surfaces, and every `.map` 404s. Record the negative; move
to `.git`/`.env`/`web-triage`.

## A flag shape in source — the flag?

A *candidate* — `pre-flag` it, prove it against a live/artifact
response. A `const FLAG` in the source is not a submission until it
passes the gate.

## Catalogue or verified?

Catalogue — no local verified solve. Standard published knowledge until
a real map-led solve lands in `../field-notes.md`.
