# Field checklist — the printable operator list

## Before you start

- [ ] the app is a SPA / ships a JS bundle
- [ ] `bundle_miner` is the tool — `python3 tools/web/bundle_miner.py --selftest` passes
- [ ] `$BASE` and any session `$C` are set

## Inventory

- [ ] entry page fetched; every `<script src>` deduped
- [ ] `_buildManifest`/`asset-manifest`/`sw.js` fetched for lazy chunks
- [ ] build fingerprinted (webpack/CRA/Next/Vite/Vue/Angular/esbuild)
- [ ] vendor/runtime chunks identified to skip

## Map

- [ ] `sourceMappingURL` read on every tail
- [ ] `<bundle>.js.map` + `/static/maps/` + `SourceMap` header + inline probed
- [ ] real map confirmed = `application/json` + `{"version":3`
- [ ] `sourcesContent` reconstructed to `--out` where present

## Mine

- [ ] `bundle_miner --url --out` run (or `--file`/`--map` + `-H`)
- [ ] endpoints extracted from EVERY bundle
- [ ] secrets extracted + `--show-secrets`/`--context`
- [ ] config/env/flags extracted
- [ ] routes extracted (client + server)
- [ ] comments/sinks grepped in recovered source
- [ ] `strings`+shape-grep on obfuscated bundles

## Triage

- [ ] leads ranked: secret > hidden-ep > flag > internal > sink > flag-shape > route > public
- [ ] endpoints deduped across chunks

## Verify

- [ ] every endpoint `curl`'d — real/404/catch-all?
- [ ] every secret probed — authenticates/dead/publishable?
- [ ] every flag's endpoint probed — server-enforced/client-only?
- [ ] every internal host noted for SSRF
- [ ] every flag-shape `pre-flag`'d
- [ ] every lead recorded: file + verbatim string + result

## Route + record

- [ ] each live lead → its class (idor/sqli/ssrf/file-read/auth-session/logic/...)
- [ ] each dead lead → a recorded negative
- [ ] a clean "mined, nothing actionable" if the route is dead
- [ ] adjacent surface probed (`.git`/`.env`/backups) if `.map` present

## Do-not

- [ ] no whole-bundle read into context
- [ ] no unverified claim presented as a finding
- [ ] no "recovered source" claim on a map-less grep
- [ ] no executing recovered source
- [ ] no re-mining a dead bundle
- [ ] no catalogue shape presented as "worked here"
