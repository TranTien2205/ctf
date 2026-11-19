# Per-target — what each mined artifact is worth

## Per artifact type

| Artifact | What it yields | Priority |
|---|---|---|
| a recovered `sourcesContent` file | real commented source — sinks, logic, keys | highest |
| an endpoint string | a real route the UI may hide | high |
| a route path (client) | an SPA page — maybe a server endpoint | high |
| a secret candidate | a key/token — verify live | high |
| a feature flag / config | a server-unenforced gate | medium |
| an internal URL/host | an SSRF/infra target | medium |
| a source file name (no content) | structure — a probe target | medium |
| a minified identifier | an obfuscation artifact | low |
| a `node_modules` source | a dependency — `--skip-node-modules` | low |

## Per find → class

| The find | Route to |
|---|---|
| endpoint with an object id | `../web-idor/` |
| endpoint with a query body | `../web-sqli/` / `../web-nosqli/` |
| a template-rendered param | `../web-ssti/` |
| a server-side fetch URL | `../web-ssrf/` |
| a file/download path | `../file-read-primitives/` |
| a verified key/token | `../web-auth-session/` |
| admin route / feature flag | `../web-logic-flaw/` / `../web-mass-assignment/` |
| internal host | `../web-ssrf/` |
| a GraphQL endpoint | `../web-graphql/` |
| a flag-shaped string | `pre-flag` gate |

## Per bundle region

| Region | Holds |
|---|---|
| `main`/`app` bundle | routes table, config, entry logic |
| page/route chunk | the route's logic, its endpoints |
| `chunk-vendors`/`vendor` | dependencies — skip for recon |
| `runtime`/`webpack` | the loader — skip |
| `sw.js`/service worker | precache manifest — every asset |
| `config.js`/`env.js` | keys, flags, env values |

## Per framework target

| Framework | Where the signal is |
|---|---|
| webpack/CRA | `main.[hash].js` + numbered chunks |
| Next.js | `_buildManifest.js` + `pages/*.js` chunks |
| Vite | `assets/index-[hash].js`, dev paths |
| Vue | `app.` + `chunk-vendors.` + route chunks |
| Angular | `main.` + lazy module chunks |
