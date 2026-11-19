# Workflow (deep) — the full operational sequence

## The six-phase pass

```
PHASE 1  INVENTORY   every script + the manifest
PHASE 2  MAP         probe every map route per bundle
PHASE 3  MINE        bundle_miner / targeted grep
PHASE 4  TRIAGE      rank the leads by value
PHASE 5  VERIFY      each lead live
PHASE 6  ROUTE       each verified lead to its class
```

## Phase 1 — inventory (≤5 min)

```bash
curl -s "$BASE/" > entry.html
grep -oE 'src="[^"]+\.js[^"]*"' entry.html | sort -u          # the bundle set
grep -oE '"buildId":"[^"]+"' entry.html                        # Next buildId
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"          # every route+chunk
```

The inventory is complete only when every script AND every manifest-
named lazy chunk is listed.

## Phase 2 — map probe (≤5 min)

```bash
for b in $BUNDLES; do
  curl -s "$BASE$b" | tail -c 300 | grep -oE 'sourceMappingURL=.+'
  curl -s -o /dev/null -w "$b.map %{http_code} %{content_type}\n" "$BASE$b.map"
done
```

A `200 application/json` → reconstruction; `text/html` → catch-all;
`404` → string mine that bundle.

## Phase 3 — mine (≤15 min)

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
# or for a session-gated app
python3 tools/web/bundle_miner.py --url "$BASE/" -H "Cookie: $C" --out recovered/
```

`bundle_miner` crawls, guesses maps, reconstructs `sourcesContent`, and
inventories endpoints + routes + flags + `process.env` + secret
candidates. Read its output sections in value order: endpoints, secrets,
routes, recovered sources.

## Phase 4 — triage

Rank the leads by exploit value:

1. a live secret/key → `web-auth-session`
2. a hidden endpoint with a param → `web-idor`/`web-sqli`/etc.
3. a feature flag / admin route → `web-logic-flaw`
4. an internal host → `web-ssrf`
5. a recovered-source sink → its class
6. a flag-shaped string → `pre-flag`

## Phase 5 — verify

Each lead's falsifier is the live check — the endpoint responds, the
secret authenticates, the flag is real. A lead is real only while its
falsifier has not fired.

## Phase 6 — route

Every verified lead routes to its class; every dead lead is a recorded
negative. The map pass ends when every lead is verified-or-dead — the
exploit is the routed class, not more mining.

## The handoff record

Record each lead: source file + verbatim string + live result + routed
class. A lead without its source file is not traceable.
