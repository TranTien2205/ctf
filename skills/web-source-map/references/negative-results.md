# Negative results — recording the mined-but-empty bundle

## What a clean negative looks like

The bundle was mined end to end and produced nothing usable:

- every endpoint string 404'd or was public-by-design
- every secret candidate failed the live check
- every route was a client-side route, not a server one
- the map 404'd on every guess and no `sourceMappingURL` existed
- the strings were opaque (no URLs, no params, no flags, no keys)

That is a *result* — record it so the next solver does not re-mine the
same bundle hoping the strings changed.

## The record shape

```json
{
  "layer": "web-source-map",
  "what_was_mined": "main.js + 4 chunks, .map 404, no sourcesContent",
  "endpoints_found": ["<list>"],
  "endpoints_dead": ["<list>"],
  "secret_candidates": 0,
  "verdict": "negative — nothing actionable in the bundle"
}
```

## The per-string negative

Each lead the map produces gets its own record when it fails:

| Lead | Result |
|---|---|
| `/api/internal` | 404 live — dead client route |
| `apiKey` candidate | not a real key — publishable `pk_live` |
| `feature.admin` flag | server-side gated — UI flag only |
| `sourcesContent` file | read, no sink — public code |

A dead lead is a measurement, not a failure — it closes that path.

## The "map gave nothing but source exists" case

The map's file names exist (`src/api/secret.js`) but `sourcesContent` is
null — you have the structure, not the text. Record it as a partial:
the file *names* are leads for a `file-read-primitives` or hosted-path
probe, but the recovery itself was a negative.

## The anti-pattern: re-mining

A mined bundle does not get re-mined. If the first pass produced
nothing, a second pass on the same bundle produces the same nothing —
the strings do not change. The next layer is the endpoint's own class,
or a different recon surface (`.git`, `.env`, backups, `web-triage`).
