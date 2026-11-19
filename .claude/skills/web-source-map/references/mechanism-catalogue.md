# Mechanism catalogue — the complete sub-mechanism reference

## Discovery

| Mechanism | What it finds | How |
|---|---|---|
| entry inventory | the bundle set | `<script src>` grep + modulepreload |
| manifest inventory | every route+chunk | `_buildManifest`/`asset-manifest`/`sw.js`/`precache` |
| build fingerprint | the bundler/framework | `webpackChunk`/`import.meta`/path patterns |
| map recovery | the `.map` | `sourceMappingURL`/sibling/header/inline |
| source reconstruction | `sourcesContent` → real source | decode + scheme-normalise + traversal-reject |

## Mining

| Mechanism | What it mines | How |
|---|---|---|
| endpoint | the route table | fetch/axios/`"/..."`/route greps |
| param | the injection points | `?x=`/`{x:`/`append`/`body` greps |
| secret | credential candidates | prefix/assign/`process.env`/`-----BEGIN` greps + entropy filter |
| flag/gate | the gated surface | `feature.`/`flags.`/`meta.`/`isAdmin` greps |
| config | env/config values | `process.env`/env prefixes/`window.__`/`__NEXT_DATA__` |
| route | the client route table | `path:`/`component:`/`loadChildren`/`_buildManifest` |
| structure | the app layout | `sources` file names |
| comment | dev notes/flag | `TODO`/`secret`/`flag{`/console greps on source |
| sink | the vuln's class | `eval`/`innerHTML`/`exec`/`fetch`/deserialize greps |
| GraphQL | the schema hints | `/graphql`/query/fragment greps |

## Verify/route

| Mechanism | Does | How |
|---|---|---|
| lead triage | ranks the leads | secret > hidden-ep > flag > internal > sink |
| live verify | falsifier per lead | `curl` endpoint/`Authorization`/`pre-flag` |
| route | lead → its class | per-param/per-endpoint/per-secret matrices |

## Context

| Mechanism | Does | How |
|---|---|---|
| adjacent disclosure | probes `.git`/`.env`/backups | the lax-deployment signal |
| authenticated bundle | mines behind the login | `-H "Cookie: $C"` |
| dev-build mining | the richer dev bundle | `webpackHotDevClient`/`?env=dev`/`.dev` host |
| deobfuscation | reads a resistant bundle | beautify/strings/array-decode/deobfuscator |

## The catalogue rule

Every mechanism is a named, bounded, falsifiable step — the pass is a
sequence of mechanisms, each with its own yield and its own falsifier.
The corpus's `mechanism-index.md`/`mechanism-map.md`/`mechanism-index-deep.md`/
`per-mechanism-deep.md` map them all.
