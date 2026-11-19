# Workflow — the bundle-mining sequence

## The ordered probe

```bash
# 1. the entry page's script inventory
curl -s "$BASE/" | grep -oE 'src="[^"]+\.js[^"]*"' | sort -u
# 2. every bundle, not just the first
for s in $(curl -s "$BASE/" | grep -oE 'src="([^"]+)\.js' | sed 's/src="//'); do
  curl -s -o "bundle_$(basename $s)" "$BASE$s"
done
# 3. mine them with the tool (endpoints + secrets + map recovery)
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

The sequence: entry → script list → fetch all → `bundle_miner` →
recovered sources + endpoint inventory + secret candidates.

## The decision after the map

| Map exists | Path |
|---|---|
| `sourcesContent` present | read the recovered source — real logic, not strings |
| map but no `sourcesContent` | the file names + structure — grep the bundle for those names |
| no map | string mining only — endpoints, params, flags, secrets |

## The output triage

`bundle_miner` emits: endpoint inventory, route paths, feature flags,
secret candidates, recovered sources. Triage by value:

1. **a live endpoint the UI hides** → `../web-idor/`/`../web-logic-flaw/`
2. **a verified secret/key** → `../web-auth-session/`
3. **an internal URL/host** → `../web-ssrf/`
4. **a feature flag or admin route** → `../web-logic-flaw/`
5. **original source with a sink** → the matching bug-class skill

## The grep-not-read budget

Never read the whole minified bundle into context — it is megabytes.
Grep for the specific token, or let `bundle_miner` inventory it. The
exception is recovered `sourcesContent`, which is real source.

```bash
# targeted, not whole-file
grep -oE '"/[A-Za-z0-9_./?=&{}:-]+"' bundle.js | sort -u | head -50
```

## The recording discipline

Every endpoint/secret/route the map produces is a *candidate* — record
each, then verify the ones that matter live. A verified find goes
through `hooks.py post-probe`; a dead candidate is a negative result.

## When the map is the flag

Some challenges hide the flag directly in the bundle or a recovered
source — a comment, a `const FLAG`, an env value. A flag-shaped string
there is still a *candidate* — `tools/hooks.py pre-flag` before treating
it as the flag, and a live/artifact response is the proof.

## The falsifier for the whole route

The bundle is mined and produces nothing: no hidden endpoint, no
secret, no route, no flag-shaped string, the map 404s, the strings are
opaque. That is the route dead — record it and move to a different
recon layer, not a second pass on the same bundle.

## Bound the pass

Bundle mining is recon, not the exploit — bound it: one entry fetch,
one `bundle_miner` run, targeted greps on the output. Do not spend the
challenge budget re-reading the same minified code; if the bundle gave
its endpoints, the next layer is the endpoint's own class.
