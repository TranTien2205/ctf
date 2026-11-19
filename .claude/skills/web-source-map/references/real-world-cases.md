# Real-world cases — the published shapes

## Catalogue note

Standard published knowledge — not solved in this repository. Record a
real solve to promote the class.

## The Next.js manifest leak

`_buildManifest.js` (and older `_buildManifest.js` / page manifests)
enumerates every route — `/admin`, `/api/internal`, `/debug` — routes
no link reaches. A `grep` of the manifest + a probe of each named route
surfaces hidden endpoints the UI gates. Published repeatedly; the
manifest is a route map the deployment leaks.

## The shipped `.env` / `config.js`

`config.js` / `env.js` / `__NEXT_DATA__` carry `REACT_APP_API_KEY`,
`NEXT_PUBLIC_SECRET`, a Firebase config, a JWT — build-inlined values
meant to be "config" that are really credentials. The `NEXT_PUBLIC_` /
`REACT_APP_` prefix marks them as *intended* public — but devs ship
real secrets under the same prefix. Verify each.

## The `.map` → full source

A deployed `main.[hash].js.map` with `sourcesContent` returns the
entire commented source — the classic CTF/info-disclosure shape. The
source names sinks, keys, and the flag. Many public writeups start
"the .js.map gave the whole app".

## The `process.env` / webpack-inlined secret

`process.env.SECRET` / `DefinePlugin`-inlined values land in the bundle
as literals. A build that inlines a server-side secret into client
code is a real leak — grep for `process.env` and the assignment
patterns.

## The lazy-admin chunk

An admin module lazy-loaded as a numbered chunk (`[n].chunk.js`) — the
UI loads it only for admins, but the file is public. Fetching the chunk
reveals the admin routes/endpoints the UI never rendered. The
`_buildManifest` names it.

## The flag-in-source CTF shape

The flag sits in a comment, a `const FLAG`, an env var the build
inlined — `bundle_miner` or a `flag{` grep surfaces it; `pre-flag`
gates it. A very common CTF web pattern.

## The adjacent `.git`/`.env`

A host shipping `.map` often ships `.git`, `.env`, backups — the map is
the lax-deployment signal that probes the broader disclosure surface.
The map and the `.git` are two doors on the same unlocked house.
