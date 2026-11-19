# Mechanism (deep) — the map format and the recovery math

## The source-map spec (v3)

A `.map` is JSON:

```json
{
  "version": 3,
  "file": "main.js",
  "sourceRoot": "",
  "sources": ["webpack://app/./src/index.js"],
  "sourcesContent": ["import ..."],
  "names": ["fetch", "api"],
  "mappings": "AAAAA,..."
}
```

- **`mappings`** — VLQ base64 position map (generated_line;generated_col;
  source_idx;orig_line;orig_col;name_idx). Recon rarely needs it — it
  locates *which* source a minified token came from.
- **`sources`** — the original paths, each potentially carrying a
  `sourceRoot` prefix and a bundler scheme (`webpack://`, `../`).
- **`sourcesContent`** — the original file text, index-aligned with
  `sources`. This is the gold — the full source, comments and all.

## The recovery algorithm

```python
import json
m = json.load(open('m.js.map'))
for i, src in enumerate(m['sources']):
    content = (m.get('sourcesContent') or [None]*len(m['sources']))[i]
    path = strip_scheme(src)            # webpack://app/./src/x.js -> src/x.js
    if escapes_out_dir(path):           # a sources traversal -> reject
        reject(path)
    if content:
        write(out/path, content)
```

`bundle_miner --source-scheme normalise` strips the scheme; a `sources`
path that escapes `--out` (`../../..`) is rejected and counted — the
map is attacker-controlled and a crafted map could otherwise write
outside the recovery directory.

## The scheme problem

`sources` carry bundler schemes that are not filesystem paths:

- `webpack://app/./src/index.js` → strip `webpack://app/` → `src/index.js`
- `../src/index.js` → a relative path, may traverse
- `src/index.js` → already a path
- `file:///src/index.js` → a file URL

`normalise` resolves them to writable paths under `--out`; `reject`
refuses a scheme it cannot make safe.

## The `sourcesContent`-absent case

A map with `sources` but no `sourcesContent` (deployments strip it to
save size) gives the file *names* and structure, not the text. The
`names` + `mappings` still recover the original identifiers, and the
file names are leads — the structure without the source.

## The inline-map decode

`//# sourceMappingURL=data:application/json;base64,<b64>` — the map is
the comment itself. `bundle_miner` decodes it; by hand, base64-decode
the segment after `base64,`.

## The header-based map

`SourceMap:` / `X-SourceMap:` response headers name the map without a
comment — `bundle_miner` checks these on the bundle response.
