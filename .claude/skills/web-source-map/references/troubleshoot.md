# Troubleshoot — when the map does not cooperate

## The map 404s

- no `sourceMappingURL` in the bundle tail — check the *last* bytes,
  not the whole file (`tail -c 300`)
- the `.map` is at a different path — try `<bundle>.js.map`,
  `<bundle>.map`, the same dir, `/static/maps/`
- production disabled sourcemaps — the common case; fall back to string
  mining
- a `200` with `text/html` is a catch-all, not a map — check content
  type

## The bundle has no strings

- it is the *vendor/runtime* bundle — the app logic is in a different
  chunk (`app.`, `main.`, a page chunk); mine all of them
- it is obfuscated beyond minification (string arrays, control-flow
  flattening) — `strings` + targeted grep still surfaces literals
- it is a WASM-backing app — the logic is in `.wasm`, not `.js`

## bundle_miner finds nothing

- the entry page's scripts were not crawled — `--max-scripts` caps at
  25; a lazy-loaded chunk is missed. Feed `--file`/`--map` directly
- the map needs auth — `-H "Cookie: ..."` for a session-gated app
- `--no-sibling-guess` was passed — the sibling map is skipped
- `--html-parser regex` missed a script tag — `--html-parser bs4` or a
  direct `--file`/`--map`

## The recovered source is empty

- the map had `sources` but no `sourcesContent` — file names only
- the `sources` paths were rejected as traversals — check
  `bundle_miner`'s count of rejected paths
- `--source-scheme reject` refused a `webpack://` path — use
  `normalise` to strip the scheme

## The "secret" is a false positive

- minified identifier, hash, or class name — check `--context`/`--lookahead`
  for the assignment it lives in
- a publishable client key (`pk_live_`, a public Firebase config) —
  meant to be public; verify before claiming
- the live check fails — the key is dead/revoked; not a finding

## The endpoint 404s

- a client-side route (react-router path), not a server endpoint
- a renamed/dead code path — the string outlived the route
- a different host/prefix — `api.example.com` vs `example.com/api`
- needs auth — probe with the session

## The honest check

When the map yields nothing, the check is: did I mine *every* bundle
the page loads (not just `main`), did I probe *every* `.map` sibling,
did I grep for the *specific* tokens (endpoints, params, secrets), or
did I read a chunk and stop. The common miss is `main`-only mining.
