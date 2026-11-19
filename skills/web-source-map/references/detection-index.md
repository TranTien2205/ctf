# Detection index — every signal, indexed

## By layer

| Layer | Signals |
|---|---|
| entry page | `<script src>`, `__NEXT_DATA__`, `data-*`, SPA root `<div>` |
| bundle tail | `//# sourceMappingURL=`, inline `data:` map |
| bundle head | `webpackChunk`, `__webpack_require__`, `(function(){` IIFE |
| bundle body | endpoint strings, secrets, flags, routes |
| response headers | `SourceMap:`, `X-SourceMap:`, `content-type` |
| manifest | `_buildManifest.js`, `asset-manifest.json`, `precache` |
| adjacent | `.map`, `.git`, `.env`, `config.js`, backups |

## By goal

| To find | The signal |
|---|---|
| every endpoint | fetch/axios call sites, `"/api/..."` literals, route defs |
| every route | `path:`/`component:`, `_buildManifest`, page chunks |
| every secret | JWT/`AKIA`/`sk_` prefixes, `apiKey`/`token` assigns, `process.env` |
| every flag | `feature.`/`flags.`/`config.`/`debug`/`internal` |
| the real source | `.map` + `sourcesContent` → `--out` |
| the app structure | `sources` file names, `src/` layout |
| the flag itself | `flag{`, `const FLAG`, comment, env value |

## By tool output

`bundle_miner` emits: the endpoint inventory, the route list, the
feature flags, the `process.env` refs, the secret candidates with
file+line, and the recovered `sourcesContent` tree. Read its output
sections in that order — endpoints and secrets first (highest value),
recovered sources for the sink hunt.

## The index rule

The map's value is completeness — it enumerates the *whole* client
surface, not a sample. Index every lead before triaging; a partial
read misses the hidden admin chunk.
