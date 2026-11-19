# Mechanism index — the recon sub-mechanisms

## The inventory mechanism

Enumerate every JS asset the app ships — the entry page's `<script src>`,
the manifest's route list, the service worker's precache. The bundle
set is the surface; miss a chunk and you miss its endpoints.

## The map-recovery mechanism

Find and decode the `.map`: the `sourceMappingURL` comment, the
sibling `<bundle>.js.map` guess, the inline `data:` URI, the
`X-SourceMap`/`SourceMap` response header. `bundle_miner` tries all
of these.

## The reconstruction mechanism

Decode `sources` + `sourcesContent` → the original file tree. Strip the
bundler scheme (`webpack://`), reject a `sources` path that escapes
`--out` (a traversal). Yields real source, not strings.

## The endpoint-mining mechanism

Extract every URL/path literal: fetch/axios call sites, bare `"/..."`
strings, `api/` prefixes, route definitions. The client's own route
table — the real endpoint list.

## The secret-mining mechanism

Extract high-entropy and structurally-keyed strings: JWTs, `AKIA`,
`sk_/pk_`, `apiKey`, `token`, private-key blocks, `process.env`.
Entropy + context filter; every candidate is verified live.

## The flag-mining mechanism

Extract `feature.*`/`flags.*`/`config.*`/`debug`/`internal` gates — the
switches the client checks. Each names a gated feature + its endpoint.

## The structure-mining mechanism

`sources` file names (even without content) map the app's internal
layout — `src/api/`, `src/config/`, `src/admin/` — probe targets and
a `file-read` hint.

## The config-mining mechanism

`config.js`, `env.js`, `process.env.*`, `__NEXT_DATA__` — the
build-inlined config: API bases, keys, flags, hosts.
