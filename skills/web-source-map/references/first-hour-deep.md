# First hour (deep) — the timed operator sequence

## Minute 0-5: inventory

Fetch the entry page. List every `<script src>` — dedupe. Fingerprint
the build (`/_next/` → Next, `/static/js/` → CRA, `/assets/` → Vite).
Fetch `_buildManifest.js`/`asset-manifest.json`/`sw.js` — the
manifest's route+asset list is the complete inventory, including the
lazy chunks `main` misses.

## Minute 5-12: the map probe

For each bundle: read the `sourceMappingURL` tail, probe
`<bundle>.js.map`, check the `SourceMap` header, decode an inline map.
A `200 application/json` `{"version":3` → reconstruction; a
`text/html` → catch-all; `404` → string mine.

## Minute 12-25: `bundle_miner`

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
# or for a session-gated app
python3 tools/web/bundle_miner.py --url "$BASE/" -H "Cookie: $C" --out recovered/
```

It crawls, guesses maps, reconstructs `sourcesContent`, inventories
endpoints + routes + flags + secrets. Read the output in value order:
endpoints, secrets, routes, recovered sources.

## Minute 25-40: mine + triage

- `sourcesContent` present → read recovered source for sinks/keys/flag
- no map → grep every bundle for endpoints/params/secrets/flags
- `--show-secrets` + `--context` for candidates
- rank: live secret > hidden endpoint > flag > internal > sink >
  flag-shape > client-route > public

## Minute 40-50: verify

- each endpoint — `curl` live; real response or 404/catch-all?
- each secret — `Authorization` probe / JWT decode
- each flag — probe the gated endpoint; server-enforced or client-only?
- each internal host — an SSRF reach target
- each flag-shape — `pre-flag`

## Minute 50-60: route + record

- each verified lead → its class
- each dead lead → a recorded negative (file + string + falsifier)
- a clean "mined, nothing actionable" if the route is dead

## The stop conditions

- every lead verified-or-dead → recon done; the exploit is the routed
  class
- the route is dead → record + move to `.git`/`.env`/`web-triage`
- a flag candidate → `pre-flag`; submit if it passes

## The one rule for the hour

The map is recon, not the exploit — it names the target, the routed
class closes it. Do not spend the hour re-reading the bundle; verify,
route, and move.
