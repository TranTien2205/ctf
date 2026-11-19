# Per-target (deep) — the value and route per mined artifact

## The value ranking

| Artifact | Value | Why |
|---|---|---|
| a live credential | highest | immediate authenticated reach |
| a hidden endpoint with a param | high | an injection/IDOR target |
| a recovered `sourcesContent` file | high | real commented source — sinks, keys |
| a feature flag / gated route | high | a server-may-not-enforce gate |
| an internal host/URL | high | an SSRF reach target |
| a secret *candidate* | medium-high | until it verifies |
| a route path (client) | medium | maybe a server endpoint |
| a source file name | medium | a probe target, layout |
| an endpoint string | medium | a claim until live |
| a `node_modules` source | low | a dependency — skip |
| a minified identifier | low | an obfuscation artifact |
| a publishable `pk_`/`NEXT_PUBLIC_` | low | meant to be public |

## The route per artifact

| Artifact | Route |
|---|---|
| endpoint `/api/x/{id}` | `web-idor` |
| endpoint `?q=`/`?search=`/`?filter=` | `web-sqli`/`web-nosqli` |
| endpoint `?template=`/`?render=` | `web-ssti` |
| endpoint `?url=`/`?target=`/`/proxy` | `web-ssrf` |
| endpoint `/file/`/`?file=`/`?path=` | `file-read-primitives` |
| endpoint `/graphql` | `web-graphql` |
| endpoint `/admin`/`/internal` | `web-logic-flaw`/`web-idor` |
| endpoint `/upload` | `web-file-upload` |
| a verified key/token | `web-auth-session` |
| an internal host | `web-ssrf` |
| a `role`/`is_admin`/`feature` param | `web-mass-assignment`/`web-logic-flaw` |
| a recovered-source `eval`/`innerHTML` | `web-command-injection`/`web-xss` |
| a recovered-source `deserialize`/`pickle` | `web-deserialization` |
| a recovered-source `exec`/`spawn` | `web-command-injection` |
| a recovered-source `fetch`/`requests` | `web-ssrf` |
| a `__proto__`/merge param | `web-prototype-pollution`/`web-mass-assignment` |
| a flag-shaped string | `pre-flag` gate |

## The param-semantic route

| Param name | Route |
|---|---|
| `id`/`uid`/`pk` | `web-idor` |
| `file`/`path`/`name` | `file-read-primitives` |
| `url`/`uri`/`callback`/`webhook` | `web-ssrf` |
| `q`/`query`/`search`/`filter`/`sort` | `web-sqli`/`web-nosqli` |
| `redirect`/`next`/`return_to` | `web-open-redirect` |
| `token`/`key`/`secret`/`otp` | `web-auth-session` |
| `role`/`admin`/`is_admin`/`permission` | `web-mass-assignment` |
| `amount`/`price`/`balance`/`discount` | `web-logic-flaw` |
| `__proto__`/`constructor`/`prototype` | `web-prototype-pollution` |

## The one-lead outcome

The whole pass is justified by ONE hidden endpoint or live key — the
triage's job is to surface that one lead among the noise.
