# Operator notes — the field-tested lessons

## The bundle is a spec, not a black box

Every endpoint, route, param, and config the client needs is in the
bundle — read it like a spec. The attacker who greps the bundle knows
the surface the attacker who guesses does not.

## The manifest is the inventory

`_buildManifest`/`asset-manifest`/`sw.js`/`precache` enumerate every
asset and route — including the lazy/admin chunks `main` misses. Fetch
the manifest before deciding the bundle is thin; the manifest is the
complete list.

## The lazy chunk is the gold

The interesting endpoint is most often in a lazy-loaded module — the
admin/feature chunk loaded on a gated route. The chunk is public; only
the *load* is gated. Fetch every lazy chunk.

## `main`-only mining is the common miss

The single most common failure: mining `main` and stopping. The route
table is in `main`, but the hidden endpoint is in a page chunk or a
lazy module. Mine every chunk the page + manifest name.

## The `.map` is the bonus, not the requirement

Production disables sourcemaps — the common case. String mining yields
endpoints/params/secrets/flags regardless. Do not stop because there is
no map.

## The secret is a candidate until it authenticates

`pk_live_`/`NEXT_PUBLIC_`/a Firebase `apiKey` is publishable — meant to
be public. A secret leaks only when it verifies — it authenticates or
decodes to real claims. Verify before claiming.

## The endpoint is a claim until it responds

`/api/admin` in the bundle may be a dead client route, a renamed path,
or a react-router path. The `curl` live check is the falsifier; a `404`
means the string outlived the route.

## The gate is client-side until the server checks

`PrivateRoute`/`meta.requiresAuth`/`feature.X` are client-side — the
code and endpoint are shipped anyway. Probe the gated endpoint
directly; the server may not enforce it.

## The map is the lax-deployment signal

A `.map` presence means the deployment ships debug artifacts — probe
`.git`, `.env`, backups, `src/`, `static/maps/`. The map is one door;
the adjacent surface is the rest of the unlocked house.

## Do not read the bundle into context

Megabytes of minified code drowns context — grep for the token or let
`bundle_miner` inventory it. Read only recovered `sourcesContent`
whole.

## The source is attacker-controlled

A recovered `sourcesContent` may be planted; a `sources` path is a
traversal (rejected, not recovered). Read the source; never execute it.

## The negative is a measurement

A mined bundle that gives nothing actionable is a clean result — record
it with the falsifier that fired; the next solver does not re-walk it.
