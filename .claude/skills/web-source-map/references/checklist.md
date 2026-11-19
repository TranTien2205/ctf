# Checklist — the bundle-mining pass

## Discover

- [ ] fetch the entry page, list every `<script src>` it loads
- [ ] fingerprint the build (Next/CRA/Vite/Vue/Angular/webpack)
- [ ] enumerate every chunk, not just `main`
- [ ] for Next.js, fetch `_buildManifest.js` for the full route list
- [ ] probe each `<bundle>.js.map` sibling + the `sourceMappingURL`

## Mine

- [ ] run `bundle_miner --url <page> --out recovered/` (or `--file`/`--map`)
- [ ] if a map: reconstruct `sourcesContent`, read the recovered source
- [ ] if no map: grep each bundle for endpoints, params, flags, secrets
- [ ] check `__NEXT_DATA__` / `config.js` / `env.js` for keys and flags
- [ ] `--show-secrets` for the secret candidates

## Triage the leads

- [ ] each endpoint string → probe it live (not a client-only route)
- [ ] each secret candidate → verify it authenticates
- [ ] each feature flag → find its endpoint, test the gate
- [ ] each internal URL → an SSRF reach target
- [ ] a flag-shaped string → `pre-flag` gate

## Route

- [ ] endpoint with an id → `web-idor`
- [ ] a query body → `web-sqli`/`web-nosqli`
- [ ] a verified key → `web-auth-session`
- [ ] an internal host → `web-ssrf`
- [ ] an admin route/flag → `web-logic-flaw`/`web-mass-assignment`

## Record

- [ ] every lead's source file + verbatim string
- [ ] the dead leads (404'd endpoints, failed keys) as negatives
- [ ] a clean "mined, nothing actionable" if the route is dead

## Do not

- [ ] read the whole minified bundle into context
- [ ] claim "recovered source" on a string grep (map only)
- [ ] treat a bundle string as a real endpoint without a live probe
- [ ] treat a secret candidate as a leak without verification
- [ ] re-mine a dead bundle
