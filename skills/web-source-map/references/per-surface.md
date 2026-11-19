# Per-surface — where in the bundle each signal lives

## The route table surface

`path:`/`component:`/`Route`/`createRouter` — the SPA's own route list.
Mine it first: it names every page including hidden ones.

## The fetch/axios surface

`fetch(`, `axios.get`, `axios.post`, `.ajax`, `XMLHttpRequest` — every
call site names an endpoint. Grep the call sites; the argument is the
URL. `bundle_miner` inventories these.

## The config surface

`config.js`, `env.js`, `constants.js`, `process.env.*`,
`REACT_APP_*`, `VUE_APP_*`, `NEXT_PUBLIC_*` — the build-inlined config:
keys, flags, API bases, hosts. The highest-value string surface.

## The feature-flag surface

`feature.`, `flags.`, `enabled:`, `debug`, `beta`, `internal` — gates
the client checks. Each names a gated feature + the endpoint behind it.

## The auth surface

`token`, `Authorization`, `Bearer`, `localStorage.setItem`, `jwt`,
`session` — where the client stores and sends credentials. A hardcoded
token here is a live credential candidate.

## The endpoint-string surface

Bare `"/api/..."`, `"/v1/..."`, `"/internal/..."` literals — endpoints
not reached through a fetch helper. A blanket `"/..."` grep catches the
ones the call-site grep misses.

## The comment surface

Recovered `sourcesContent` carries the original comments — `// TODO`,
`// FIXME`, `// secret`, `// flag{`. Devs leave notes in source; the
map leaks them. Grep recovered source for `flag{`, `TODO`, `secret`,
`password`.

## The manifest surface

`_buildManifest.js`, `asset-manifest.json`, `precache-manifest.*.js` —
the build's own inventory of every asset and route. A manifest is a
route/asset map the UI does not show.
