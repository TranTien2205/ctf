# Summary — web-source-map in one pass

## What it does

Mines a single-page app's shipped JavaScript — the bundle's endpoints,
routes, params, flags, and secrets; and the `.map`'s recovered original
source — to enumerate the real attack surface the UI hides.

## The pipeline

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

entry page → script list → fetch all → `bundle_miner` → recovered
sources + endpoint/secret inventory.

## The two paths

- **map present** (`sourcesContent`) → read the real commented source
- **map absent** → string-mine every bundle for literals

## The output → class map

| Lead | Route |
|---|---|
| endpoint + id | `web-idor` |
| query body | `web-sqli`/`web-nosqli` |
| template render | `web-ssti` |
| server fetch URL | `web-ssrf` |
| file path | `file-read-primitives` |
| verified key | `web-auth-session` |
| admin route/flag | `web-logic-flaw`/`web-mass-assignment` |
| internal host | `web-ssrf` |
| GraphQL | `web-graphql` |
| flag shape | `pre-flag` |

## The four rules

1. **the map is recon, not the exploit** — it names targets, the routed
   class closes them
2. **verify every lead live** — a bundle string is a claim, not a fact
3. **a secret is a candidate** — it leaks only if it authenticates
4. **the source is attacker-controlled** — read it, never execute it,
   and a `sources` traversal is rejected, not recovered

## The evidence level

Catalogue — no local verified solve. Standard published knowledge until
a real map-led solve lands in `../field-notes.md`.
