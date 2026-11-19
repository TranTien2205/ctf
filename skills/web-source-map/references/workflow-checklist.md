# Workflow checklist — the operator's ordered pass

## Phase 1: inventory

- [ ] fetch the entry page; list every `<script src>` (dedupe)
- [ ] fingerprint the build (Next/CRA/Vite/Vue/Angular/webpack/esbuild)
- [ ] fetch `_buildManifest.js` / `asset-manifest.json` / `sw.js` for the
      lazy+full asset list
- [ ] enumerate every chunk — `main` + page chunks + lazy modules

## Phase 2: map probe

- [ ] read each bundle's tail for `sourceMappingURL=`
- [ ] probe each `<bundle>.js.map` sibling (`200 application/json`?)
- [ ] check the `SourceMap`/`X-SourceMap` response header
- [ ] decode an inline `data:` map if present
- [ ] a `200 text/html` is a catch-all — not a map

## Phase 3: mine

- [ ] `bundle_miner --url <page> --out recovered/` (or `--file`/`--map`)
- [ ] `-H "Cookie: $C"` for a session-gated bundle
- [ ] read recovered `sourcesContent` where it exists
- [ ] grep every bundle for endpoints/params/secrets/flags when no map
- [ ] `--show-secrets` + `--context` for the candidates
- [ ] grep `__NEXT_DATA__`/`config.js`/`env.js`/`process.env` for config

## Phase 4: triage

- [ ] rank leads: secret > hidden-endpoint > flag > internal > sink >
      flag-shape > client-route > public
- [ ] dedupe endpoints across chunks

## Phase 5: verify

- [ ] each endpoint — `curl` live; real response or 404/catch-all?
- [ ] each secret — `Authorization` probe / JWT decode; authenticates?
- [ ] each flag — probe the gated endpoint; server-enforced or client-only?
- [ ] each internal host — an SSRF reach target
- [ ] each flag-shape — `pre-flag` gate
- [ ] record each lead: file + verbatim string + result

## Phase 6: route + record

- [ ] endpoint+id → idor; query → sqli/nosqli; fetch-URL → ssrf;
      file → file-read; key → auth-session; flag/admin → logic/mass-assign;
      internal → ssrf; graphql → graphql; flag-shape → pre-flag
- [ ] dead leads → recorded negatives (file + string + dead response)
- [ ] a clean "mined, nothing actionable" if the route is dead

## The do-not list

- [ ] no whole-bundle read into context
- [ ] no "recovered source" claim on a string grep
- [ ] no unverified endpoint/secret claim
- [ ] no re-mine of a dead bundle
- [ ] no executing recovered source
