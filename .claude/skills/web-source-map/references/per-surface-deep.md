# Per-surface (deep) — every bundle surface and its yield

## The route-table surface

`path:`/`component:`/`Route`/`createRouter`/`RouterModule` — the SPA's
own route list. Yield: every client route + the gated-route map.
Highest structural value.

## The fetch/axios surface

`fetch(`, `axios.get`, `axios.post`, `.ajax`, `XMLHttpRequest`,
`HttpClient` — every call site names an endpoint + the params sent.
Yield: the real endpoint table + the request contract.

## The config surface

`config.js`, `env.js`, `constants.js`, `process.env.*`, env prefixes,
`window.__CONFIG__`, `__NEXT_DATA__.runtimeConfig` — the build-inlined
config. Yield: keys, flags, API bases, internal hosts. Highest secret
value.

## The feature-flag surface

`feature.`, `flags.`, `enabled:`, `debug`, `beta`, `internal`,
`isAdmin`, `meta.requiresAuth` — the client-side gates. Yield: the
gated surface + the endpoint behind each gate.

## The auth surface

`token`, `Authorization`, `Bearer`, `localStorage`, `jwt`, `session`,
`cookie`, `sign`, `verify` — where the client stores/sends credentials
+ the token format. Yield: a hardcoded token or the auth scheme.

## The endpoint-string surface

Bare `"/..."` literals not reached through a fetch helper — a `"/api/"`
grep catches what the call-site grep misses. Yield: the non-call-site
endpoints.

## The comment surface

Recovered `sourcesContent` comments — `// TODO`, `// secret`,
`// flag{`. Yield: dev notes, credentials, the flag. Only on a source
recovery.

## The manifest surface

`_buildManifest.js`, `asset-manifest.json`, `precache-manifest.*.js`,
`sw.js` — the build's asset+route inventory. Yield: the complete
asset/lazy route list.

## The env-inline surface

`process.env.*`, `DefinePlugin`, `import.meta.env.*`, `NODE_ENV` —
build-inlined env. Yield: config values, sometimes a server secret.

## The service-worker surface

`sw.js`, `workbox`, precache lists, runtime-caching rules. Yield: the
full asset inventory + cached internal routes.

## The template/HTML surface

AOT-compiled template strings, `innerHTML`/`dangerouslySetInnerHTML` —
yield: hidden routes in markup, a DOM-XSS sink hint.

## The structure surface

`sources` file names (no content) — `src/config/`, `src/admin/` —
yield: the app layout + hosted-path probes.
