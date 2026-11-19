# Troubleshooting map — the symptom → cause → fix index

## Symptom: the `.map` 404s

| Cause | Fix |
|---|---|
| no `sourceMappingURL` | check `tail -c 300`, not the whole file |
| wrong map path | try `<bundle>.js.map`, `.map`, `/static/maps/` |
| a `SourceMap` header instead | `curl -I` the bundle |
| an inline `data:` URI | base64-decode the tail |
| prod disabled maps | the common case — string mine |
| a `text/html` catch-all | not a map — check content type |

## Symptom: the bundle has no strings

| Cause | Fix |
|---|---|
| mining vendor/runtime | the app logic is `main`/`app`/page chunks |
| obfuscation | grep the string array / shape-grep / deobfuscate |
| WASM-backing | the logic is in `.wasm` |
| a thin loader | no app code — not this route |

## Symptom: `bundle_miner` finds nothing

| Cause | Fix |
|---|---|
| lazy chunk missed | `--max-scripts` cap; feed `--file`/`--map` |
| map needs auth | `-H "Cookie: $C"` |
| `--no-sibling-guess` set | remove it — the sibling is skipped |
| regex parser missed a tag | `--html-parser bs4`, or `--file`/`--map` |
| `sources` all rejected | check the traversal-rejection count |
| `--source-scheme reject` | use `normalise` for `webpack://` |

## Symptom: recovered source is empty

| Cause | Fix |
|---|---|
| `sourcesContent` null | file names only — structure leads |
| traversal rejected | check the rejection count |
| `--source-scheme reject` | `normalise` the scheme |

## Symptom: the secret is a false positive

| Cause | Fix |
|---|---|
| a minified id/hash | `--context` shows a non-secret position |
| publishable `pk_`/`NEXT_PUBLIC_` | meant public — not a leak |
| a dead/revoked key | live check fails — record negative |

## Symptom: the endpoint 404s

| Cause | Fix |
|---|---|
| a client route | probe the `/api/` prefix |
| a renamed/dead path | the string outlived the route |
| a different host/prefix | `api.x.com` vs `/api` |
| needs auth | probe with the session |
| a catch-all `200` | not a real endpoint |

## The bottom check

Did I mine *every* bundle, probe *every* map route, grep for the
*specific* tokens, verify *every* lead — or did I read one chunk and
stop? The common miss is `main`-only mining.
