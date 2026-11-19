# Source maps (deep) — the recovery mechanism in full

## The v3 spec

A `.js.map` is JSON, `version: 3`:

```json
{
  "version": 3,
  "file": "main.js",
  "sourceRoot": "webpack://app/",
  "sources": ["webpack://app/./src/index.js", "..."],
  "sourcesContent": ["import ...", "..."],
  "names": ["fetch", "api", "secret"],
  "mappings": "AAAA,SAAS,..."
}
```

- **`sources`** — the original paths (index-aligned with
  `sourcesContent`)
- **`sourcesContent`** — the original file text — the gold
- **`names`** — the original identifier names
- **`mappings`** — the VLQ position map (rarely needed)
- **`sourceRoot`** — the path prefix applied to `sources`
- **`file`** — the bundle it maps

## The `mappings` field — when it matters

`mappings` is a base64-VLQ position map:
`generated_col;source_idx;orig_line;orig_col;name_idx`. Recon rarely
decodes it — but it maps *which* source a minified token came from,
useful when `sourcesContent` is absent and you need the originating
file for a minified string.

## The `sourceRoot` + scheme resolution

A `source` resolves as `sourceRoot + source` after normalisation:

- `webpack://app/./src/index.js` → `src/index.js` (strip
  `webpack://app/` and the `./`)
- `../src/index.js` → a relative path — may traverse
- `src/index.js` → already a path
- `file:///src/x.js` → a file URL → strip the scheme

`bundle_miner --source-scheme normalise` resolves these to writable
paths under `--out`; `reject` refuses a scheme it cannot make safe.

## The traversal guard

A `sources` path that escapes `--out` (`../../..`) is a *traversal*, not
a recovery — `bundle_miner` rejects and counts it. The map is
attacker-controlled; a crafted map could write outside the recovery
dir. A map whose `sources` all traverse is not a clean recovery.

## The `sourcesContent`-absent case

`sources` present, `sourcesContent` null — the deployment stripped the
source to save size. You get the file *names* and structure — `src/api/
auth.js`, `src/config/secrets.js` — the layout, not the text. The names
are leads: the same paths may be hosted (`/src/config/secrets.js`) or
hint at a `file-read` target.

## The multi-level / chained map

A `.map` whose `sources` point to intermediate build artifacts (TS →
babel → webpack), sometimes with its own `sourceMappingURL` — a build
chain. Follow the innermost map for the true original source.

## The inline map decode

`//# sourceMappingURL=data:application/json;base64,<b64>` — the map is
the comment. `bundle_miner` decodes it; by hand, base64-decode the
segment after `base64,` (or URL-decode if it is `data:...;charset=`).

## The header-based map

`SourceMap:`/`X-SourceMap:` response headers name the map without a
comment — `bundle_miner` checks the bundle's response headers.

## The reconstruction algorithm

```python
import json
m = json.load(open('m.js.map'))
root = m.get('sourceRoot', '')
sc = m.get('sourcesContent') or [None]*len(m['sources'])
for src, content in zip(m['sources'], sc):
    path = normalise(root + src)          # strip scheme, resolve . and ..
    if escapes_out(path):                  # a traversal -> reject
        continue
    if content:
        write(out/path, content)
```
