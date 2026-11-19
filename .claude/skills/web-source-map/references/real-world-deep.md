# Real-world (deep) — the published recon patterns in detail

## Catalogue note

Published knowledge — not solved in this repository. Each pattern is the
recon shape that appeared in public writeups/bounty reports.

## The `_buildManifest` route leak

Next.js `_buildManifest.js` enumerates every page route — repeatedly the
lead in writeups where a hidden `/admin`, `/debug`, `/internal` route
surfaced. The manifest is a route map the deployment leaks; the page
chunk then names the endpoints.

## The `.map` → full source

The classic: `main.[hash].js.map` with `sourcesContent` returns the
entire commented source. Countless CTF/bounty writeups start "the
.js.map gave the whole app" — the keys, the logic, the flag. The
`sourcesContent` field is the disclosure; the map file is the vector.

## The `process.env` / DefinePlugin inline

`process.env.SECRET`, `DefinePlugin`-inlined values — a server-side
secret baked into client code as a literal. A `REACT_APP_SECRET` /
`NEXT_PUBLIC_PRIVATE` under an env prefix that carries a real credential.
The prefix marks it *intended* public; the value is not.

## The lazy-admin chunk

An admin module lazy-loaded as a numbered chunk — `import('./Admin')`
behind a role check. The file is public; the load is gated. Fetching
the chunk reveals the admin surface the UI never rendered. A recurring
"hidden admin" recon shape.

## The flag-in-source CTF shape

The flag as a `const FLAG`, a `// flag{` comment, an env-inlined flag —
the map or a `flag{` grep surfaces it; `pre-flag` gates it. A very
common CTF web recon pattern.

## The `__NEXT_DATA__` config leak

`__NEXT_DATA__.runtimeConfig` / `props` — server-injected config and
secrets serialized into the entry page. A `runtimeConfig.secret` or a
`props.internalApiKey` shipped to every visitor.

## The `.git` / `.env` adjacent

A deployment that ships `.map` ships `.git`, `.env`, backups — the map
is the lax signal; the `.git` recovers the server source, the `.env`
the credentials. The map and the `.git` are two doors on the same
unlocked house.

## The hardcoded-credential pattern

`apiKey`, `secret`, `token`, a JWT, a private key in client source —
the credential the build baked in. Repeatedly the finding in bounty
reports where a "client-side" key was really a server credential.

## The feature-flag bypass

`feature.X`/`flags.Y`/`config.debug` gating an endpoint the client
hides — the gate is client-side; probing the endpoint directly reaches
the gated behavior. The flag names the gate the server does not check.

## The service-worker manifest

`precache-manifest`/`sw.js`/`asset-manifest.json` — the full asset
inventory naming lazy/admin chunks `main` never references. A complete
asset map without crawling.
