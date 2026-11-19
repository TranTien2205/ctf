# Checklist (deep) — the exhaustive operator list

## Discovery completeness

- [ ] entry page fetched; every `<script src>` listed and deduped
- [ ] every `<link rel=modulepreload>` / `import()` hint captured
- [ ] `__NEXT_DATA__`/`buildId` parsed (Next.js)
- [ ] `_buildManifest.js`/`_ssgManifest.js`/`asset-manifest.json`/
      `precache-manifest`/`sw.js` fetched for the full asset+route list
- [ ] every lazy chunk enumerated (not just `main`)
- [ ] the build fingerprinted (webpack/CRA/Next/Vite/Vue/Angular/esbuild)

## Map completeness

- [ ] `sourceMappingURL` read on every bundle tail
- [ ] `<bundle>.js.map` + `<bundle>.map` + `/static/maps/` probed
- [ ] `SourceMap`/`X-SourceMap` header checked
- [ ] inline `data:` map decoded
- [ ] `200 text/html` catch-alls distinguished from real maps
- [ ] a real map = `application/json` + `{"version":3`

## Mining completeness

- [ ] `bundle_miner --url --out` run (or `--file`/`--map` + `-H`)
- [ ] `sourcesContent` reconstructed + read for sinks/keys/logic
- [ ] every bundle grepped: endpoints, params, secrets, flags, routes
- [ ] `--show-secrets`/`--context`/`--lookahead` for candidates
- [ ] `config.js`/`env.js`/`process.env`/env prefixes grepped
- [ ] comments grepped in recovered source (TODO/secret/flag)
- [ ] `strings`+shape-grep on obfuscated bundles
- [ ] structure/`sources` names mapped (even without content)

## Verify completeness

- [ ] every endpoint `curl`'d — real response / 404 / catch-all?
- [ ] every secret probed — `Authorization`/decode; authenticates?
- [ ] every flag's gated endpoint probed — server-enforced / client-only?
- [ ] every internal host noted for SSRF reach
- [ ] every flag-shape `pre-flag`'d
- [ ] every lead recorded: file + verbatim string + result

## Route completeness

- [ ] endpoint+id → idor; query → sqli/nosqli; fetch-URL → ssrf;
      file-path → file-read; key → auth-session; flag/admin →
      logic/mass-assign; internal → ssrf; graphql → graphql;
      param-by-name → its class; flag-shape → pre-flag
- [ ] dead leads recorded as negatives
- [ ] a clean "mined, nothing actionable" recorded if the route is dead

## The honesty checks

- [ ] no unverified claim presented as a finding
- [ ] no "recovered source" claim on a map-less grep
- [ ] no recovered source executed
- [ ] no catalogue shape presented as "worked here"
