# Source maps — the reconstruction mechanism in detail

## What a source map is

A `.js.map` is a JSON document mapping positions in the minified bundle
back to positions in the original source. Its key fields:

```json
{
  "version": 3,
  "file": "main.js",
  "sources": ["webpack://app/src/index.js", "webpack://app/src/api.js"],
  "sourcesContent": ["<the original source text>", "..."],
  "names": ["fetch", "handleClick", ...],
  "mappings": "AAAA,SAAS,..."
}
```

- `sources` — the original file paths (often a bundler scheme like
  `webpack://` or `../src/`)
- `sourcesContent` — the **original source text** — the gold: real
  commented source, not minified code
- `names` — the original identifier names
- `mappings` — the VLQ-encoded position map (usually not needed for
  recon)

## The recovery decision

| State | Path |
|---|---|
| `sourcesContent` present | the full original source — write it to disk |
| `sources` present, no `sourcesContent` | the file names + structure, not the text |
| only `mappings`+`names` | position map only — little recon value |
| no map | string mining on the bundle only |

## The reconstruction

```bash
# bundle_miner writes sourcesContent to --out
python3 tools/web/bundle_miner.py --map main.js.map --out recovered/

# the source-scheme handling: webpack:// is stripped to a real path
python3 tools/web/bundle_miner.py --map main.js.map --out recovered/ \
  --source-scheme normalise
```

`--source-scheme normalise` strips the bundler scheme (`webpack://`,
`../`) so `webpack://app/src/index.js` becomes a writable path;
`reject` refuses it. A `sources` path that escapes `--out` (a
`../../../` traversal) is rejected and counted — the map is
attacker-controlled and could otherwise write outside the recovery dir.

## When `sourcesContent` is absent

`sources` still names the original file structure — `src/api/auth.js`,
`src/config/secrets.js` — which tells you where to look. Some servers
host the original files at those paths (`/src/api/auth.js`,
`/static/js/src/...`) — worth a probe, but a 404 is the common answer.

## The manual map read

When `bundle_miner` is not the path, a map is readable directly:

```python
import json
m = json.load(open('main.js.map'))
for src, content in zip(m['sources'], m.get('sourcesContent') or []):
    if content:
        print('===', src)
        print(content[:2000])
```

## The map-as-source caveat

A `.map` is attacker-controlled data — its `sources` paths and
`sourcesContent` are whatever the build produced or a hostile build
planted. Read the recovered source; do not execute it; and a "secret"
in it is a candidate until verified live.

## The framework map shapes

| Build | Map name shape |
|---|---|
| webpack | `<bundle>.js.map`, `//# sourceMappingURL=` |
| Vite | `<asset>.js.map`, sourcemaps off in prod by default |
| CRA | `/static/js/main.[hash].js.map` |
| Next.js | per-chunk maps, `/_next/static/chunks/*.js.map` |
| Angular | `main.[hash].js.map`, often disabled in prod |

Many production builds disable sourcemaps — their absence is common,
not a failure; fall back to string mining.
