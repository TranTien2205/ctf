# Troubleshoot (deep) — the diagnostic tree

## The map 404s — the tree

```
.map 404
  +-- no sourceMappingURL in tail?    -> check `tail -c 300`, not the whole file
  +-- comment present but map path wrong? -> try <bundle>.js.map, <bundle>.map, /static/maps/
  +-- a SourceMap: header instead?    -> `curl -I` the bundle, grep sourcemap
  +-- an inline data: URI?            -> base64-decode the tail
  +-- production disabled maps?       -> the common case -> string mine
  +-- a 200 text/html catch-all?      -> not a map -> check content_type
```

## The bundle has no strings — the tree

```
no readable strings
  +-- mining the vendor/runtime bundle? -> the app logic is in main/app/page chunks
  +-- obfuscated (string array)?        -> grep the array, or deobfuscate
  +-- a WASM-backing app?               -> the logic is in .wasm
  +-- a thin loader (server-rendered)?  -> no app code to mine -> not this route
```

## bundle_miner finds nothing — the tree

```
bundle_miner empty
  +-- lazy chunk not crawled?  -> --max-scripts caps; feed --file/--map directly
  +-- map needs auth?          -> -H "Cookie: ..."
  +-- --no-sibling-guess set?  -> the sibling map is skipped
  +-- regex parser missed a tag? -> --html-parser bs4, or --file/--map
  +-- sources all rejected?    -> check the rejected-traversal count
  +-- --source-scheme reject?  -> webpack:// refused -> use normalise
```

## The recovered source is empty — the tree

```
empty recovered/
  +-- sources but no sourcesContent? -> file names only (deploy stripped)
  +-- traversal rejected?            -> check the rejection count
  +-- --source-scheme reject?        -> a webpack:// path refused
```

## The secret is a false positive — the tree

```
candidate fails
  +-- minified id/hash?          -> --context shows a non-secret position
  +-- publishable pk_live/public? -> meant to be public -> not a leak
  +-- dead/revoked key?          -> live check fails -> not a finding
  +-- a Next_PUBLIC_ value?      -> intended public -> verify what it unlocks
```

## The endpoint 404s — the tree

```
endpoint 404
  +-- a client route (react-router)? -> probe /api/ prefix
  +-- a renamed/dead path?           -> the string outlived the route
  +-- a different host/prefix?       -> api.example.com vs /api
  +-- needs auth?                    -> probe with the session
  +-- a catch-all 200?               -> not a real endpoint
```

## The honest check at the bottom

Did I mine *every* bundle, probe *every* map route, grep for the
*specific* tokens, verify *every* lead — or did I read one chunk and
stop? The common miss is `main`-only mining or a single grep.
