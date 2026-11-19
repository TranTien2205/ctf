# Detection — is there a bundle, and is there a map

## The bundle signatures

| Signal | Where |
|---|---|
| `/_next/static/` | a Next.js app |
| `/static/js/` | a create-react-app / webpack build |
| `/assets/index-[hash].js` | a Vite build |
| `//# sourceMappingURL=` | a bundle referencing its map |
| `*.js.map` reference | a map file reachable |
| `<script src=...chunk...>` | a chunked webpack/Rollup build |
| `webpackChunk`, `__webpack_require__` | webpack internals in the bundle |

The entry page's `<script src>` tags are the inventory — fetch the
entry page, list every script URL, that is the bundle set.

```bash
curl -s "$BASE/" | grep -oE 'src="[^"]+\.js[^"]*"' | sort -u
curl -s "$BASE/" | grep -oE '/[A-Za-z0-9._/-]+\.js[^"]*' | sort -u
```

## The map signatures

```bash
# the sourceMappingURL comment at the bundle's tail
curl -s "$BASE/static/js/main.[hash].js" | tail -c 300
# -> //# sourceMappingURL=main.[hash].js.map

# request the map
curl -s -o map.json -w '%{http_code}\n' "$BASE/static/js/main.[hash].js.map"
# a 200 + JSON map = source reconstruction possible
```

A `200` with `Content-Type: application/json` and a `{"version":3,...}`
body is a real map. A `200` with `text/html` is a catch-all route, not
a map — check the content type, not the status.

## The SPA fingerprints

| Framework | Fingerprint |
|---|---|
| Next.js | `/_next/static/`, `__NEXT_DATA__`, `_buildManifest.js`, `_ssgManifest.js` |
| React (CRA) | `/static/js/main.[hash].js`, `/static/css/` |
| Vue (CLI) | `/js/app.[hash].js`, `/js/chunk-vendors.[hash].js` |
| Vite | `/assets/index-[hash].js`, `/@vite/` in dev |
| Angular | `/main.[hash].js`, `runtime.[hash].js`, `polyfills` |
| webpack generic | `webpackChunk`, `__webpack_require__`, chunk ids |

## The map-presence decision

```
//# sourceMappingURL= present + .map fetches -> source reconstruction
no comment but .map guesses sibling          -> try <bundle>.js.map
no map at all                                -> string mining only
```

`bundle_miner`'s `--no-sibling-guess` controls the sibling-map guess —
by default it tries `<bundle>.js.map` even without the comment.

## The falsifier for this route

- the entry page loads no JS bundle (a server-rendered app with no SPA)
- every bundle is already-deobfuscated/unminified with no strings
- a `.map` 404s on every guess AND no `sourceMappingURL` exists

A minified bundle with no readable strings and a 404 map is the route
dead — not "try harder on the same bundle".

## Budget

Detection is cheap: one entry-page fetch, one script-list, one `.map`
probe per bundle. The mining afterward is the work — bound it by
targeting the strings/endpoints/secrets, not by reading the whole
bundle into context.
