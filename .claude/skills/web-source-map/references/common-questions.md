# Common questions

## Is this a vulnerability class?

No — it is a recon layer. It produces *leads* (endpoints, secrets,
routes, source) that route to the class that owns them. The map is the
discovery; the finding is the follow-on.

## The `.map` 404s — is the skill useless?

No — the common case. Production disables sourcemaps; fall back to
string mining on the bundle, which yields endpoints/params/flags/secrets
even without a map. The map is a bonus.

## The bundle is huge — where do I look?

Grep for the specific token (endpoint, param, secret, `flag{`) or let
`bundle_miner` inventory it. Never read the whole minified bundle into
context. Skip the vendor/runtime bundles — the app logic is in
`main`/`app`/page chunks.

## "Recovered the source" — from strings?

No — string mining on a map-less bundle yields *literals*, not source.
Only a `sourcesContent` recovery is the real commented source. Do not
claim to have "read the application" from a grep.

## A high-entropy string — a leak?

A *candidate*. `pk_live_` is publishable; a dead token is not a
finding. Verify it authenticates/decodes before presenting it as a
leaked credential.

## An endpoint string — a real route?

A *claim*. `/api/admin` may be a dead client route, a renamed path, or
a react-router path that never hits the server. Verify it responds
live before treating it as a target.

## The map's `sources` path is `../../../etc/passwd` — a read?

A *traversal*, not a recovery — `bundle_miner` rejects and counts it.
The map is attacker-controlled; a hostile `sources` path does not write
outside `--out`. Read recovered source; never execute it.

## When is the route dead?

When every bundle is mined, the strings are opaque, no endpoint/secret/
route/flag surfaces, and every `.map` 404s. Record the negative and
move to a different recon layer (`.git`, `.env`, `web-triage`).

## Catalogue or verified?

Catalogue — no local verified solve. The corpus is standard published
knowledge; a real map-led solve in `../field-notes.md` promotes it.
