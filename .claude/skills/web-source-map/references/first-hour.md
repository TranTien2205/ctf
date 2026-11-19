# First hour — the order of work on a SPA

## Minute 0-5: inventory

Fetch the entry page. List every `<script src>`. Fingerprint the build
(`/_next/` → Next, `/static/js/` → CRA, `/assets/` → Vite). That is the
bundle set — every chunk, not just `main`.

## Minute 5-15: the map probe

For each bundle, probe the `.map` sibling and read the
`sourceMappingURL` tail. A `200 application/json` starting
`{"version":3` is a real map. Next.js: fetch `_buildManifest.js` for
the full route list — it names routes no link reaches.

## Minute 15-30: `bundle_miner`

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

It crawls the scripts, guesses maps, reconstructs `sourcesContent`,
and inventories endpoints + routes + flags + secret candidates. The
output is the lead list.

## Minute 30-50: triage and verify

- endpoints → probe each live; keep the ones that respond
- secrets → `--show-secrets`, verify the candidates authenticate
- flags/config → name the gated endpoint
- internal URLs → note for SSRF
- a flag-shaped string → `pre-flag`

## Minute 50-60: route and record

Each verified lead routes to its class (`web-idor`, `web-auth-session`,
`web-ssrf`, `web-logic-flaw`, ...). Record each lead's source file and
verbatim string, and the dead leads as negatives.

## The stop conditions

- every lead verified or dead → the recon is done; the exploit is the
  routed class, not more mining
- the bundle gave nothing actionable → record the negative, move to a
  different recon layer (`.git`, `.env`, `web-triage`)
- a flag candidate → gate it, submit if it passes

## The one rule

The map is recon, not the exploit — it names the target, the routed
class closes it. Do not spend the hour re-reading the bundle.
