# Glossary

- **bundle** — the minified JavaScript the app ships (`main.js`,
  `index-*.js`), the app's client-side logic collapsed into one or more
  files
- **chunk** — a code-split piece of the bundle (`[n].chunk.js`,
  per-route); webpack/Rollup split output into a main bundle plus chunks
- **source map** (`*.js.map`) — a JSON mapping from minified positions
  back to original source; `version: 3`
- **`sources`** — the map's list of original file paths (often a
  `webpack://` or `../src/` scheme)
- **`sourcesContent`** — the map's inlined original source text — the
  real, commented source code
- **`sourceMappingURL`** — the `//#` comment at a bundle's tail naming
  its map (a URL or an inline `data:` URI)
- **minification** — removing whitespace/renaming identifiers to shrink
  the bundle; preserves string literals
- **obfuscation** — deliberate transformation (string arrays,
  control-flow flattening) to resist reading; strings still survive
- **`webpack://`** — a bundler source scheme; `bundle_miner
  --source-scheme normalise` strips it to a real path
- **vendor bundle** (`chunk-vendors`, `vendor.js`) — the third-party
  dependencies bundle; skip for app recon
- **`_buildManifest.js`** — Next.js build manifest listing every page
  route and its chunk
- **`__NEXT_DATA__`** — Next.js serialized props in the entry page
- **catch-all** — an SPA fallback route that serves the index page for
  any path; makes a `.map` request return `200 text/html`, not a map
- **feature flag** — a `feature.*`/`flags.*`/`config.*` gate the client
  checks; the server may not enforce it
- **secret candidate** — a high-entropy string that may be a key/token;
  a candidate until it verifies live
- **string mining** — grepping the minified bundle for literals
  (endpoints, params, secrets) when no map exists
- **reconstruction** — decoding a map's `sourcesContent` back to the
  original source tree (`--out`)
- **`bundle_miner`** — `tools/web/bundle_miner.py`, the sanctioned
  mining tool: crawls scripts, guesses maps, reconstructs sources,
  inventories endpoints and secret candidates
