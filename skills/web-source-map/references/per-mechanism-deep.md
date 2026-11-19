# Per-mechanism (deep) — each recon sub-mechanism in detail

## M1: the inventory mechanism

Enumerate every JS asset — entry `<script src>`, manifest route list,
service-worker precache, lazy-chunk `import()`. The bundle set is the
surface. **Falsifier**: a missed chunk = a missed surface. Depth: until
every named asset is fetched.

## M2: the map-recovery mechanism

Find the `.map` via `sourceMappingURL` comment → sibling guess →
`SourceMap`/`X-SourceMap` header → inline `data:` URI. **Falsifier**:
all four 404/`text/html` → string mine. Depth: 4 probes per bundle.

## M3: the reconstruction mechanism

`sources` + `sourcesContent` → the original tree. Normalise the
bundler scheme (`webpack://`, `../`), reject a `sources` traversal.
**Falsifier**: `sourcesContent` null → file names only. Depth: one
decode.

## M4: the endpoint-mining mechanism

Fetch/axios call sites + `"/..."` literals + route defs + `api/`
prefixes → the real route table. **Falsifier**: every string 404s →
dead leads. Depth: one grep set per bundle.

## M5: the secret-mining mechanism

JWT/`AKIA`/`sk_`/`apiKey`/`token`/`process.env`/key blocks → secret
candidates. Entropy + context + shape filter. **Falsifier**: all
candidates fail auth → dead. Depth: grep + `--show-secrets` + verify.

## M6: the flag-mining mechanism

`feature.*`/`flags.*`/`config.*`/`debug` gates → the gated surface +
endpoint. **Falsifier**: server enforces the gate → dead. Depth: grep +
flag-endpoint probe.

## M7: the structure-mining mechanism

`sources` file names → the app layout + hosted-path probes.
**Falsifier**: no hosted source, no interesting names. Depth: one
`sources` list + path probes.

## M8: the config-mining mechanism

`config.js`/`env.js`/`process.env`/`__NEXT_DATA__`/env prefixes →
config + keys + flags. **Falsifier**: all publishable. Depth: one grep
set.

## M9: the comment-mining mechanism

Recovered-source comments → TODO/secret/flag/gate notes.
**Falsifier**: comments stripped or empty. Depth: one grep on
`sourcesContent`.

## M10: the sink-mining mechanism

Recovered-source sinks (`eval`/`innerHTML`/`exec`/`fetch`/deserialize)
→ the vuln + its class. **Falsifier**: no sink / client-only. Depth:
one sink grep on recovered source.

## The mechanism order

M1 → M2 → M3 (the map path) and M4/M5/M6/M8 (the string path) are the
core. M7/M9/M10 apply to a map/source recovery. The string path is the
fallback when M2/M3 dead-end.
