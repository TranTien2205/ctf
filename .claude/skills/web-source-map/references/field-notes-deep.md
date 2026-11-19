# Field notes (deep) — what to record per challenge

## The per-challenge record shape

```json
{
  "challenge": "<name>", "event": "<event>",
  "layer": "web-source-map",
  "bundle_set": ["main.js", "2.chunk.js", "pages/admin-*.js"],
  "build": "webpack|next|vite|vue|angular|esbuild",
  "map": {"found": true, "sourcesContent": true, "files_recovered": 14},
  "leads": [
    {"string": "/api/internal", "src": "pages/admin.js",
     "verify": "200 live", "verdict": "live", "route": "web-idor"},
    {"string": "apiKey candidate", "src": "config.js",
     "verify": "401", "verdict": "dead"},
    {"string": "feature.admin", "src": "app.js",
     "verify": "403 stays", "verdict": "server-enforced"}
  ],
  "flag_shape": {"found": false},
  "adjacent": {".git": 404, ".env": 404, "backup": 404},
  "verdict": "the map produced 3 leads; 1 live (idor), 2 dead",
  "solved_via": "web-idor on /api/internal/{id}",
  "reopen_if": "the deployment ships a new bundle"
}
```

## What to record, always

- the bundle set mined (every chunk, not just `main`)
- the build fingerprint
- the map state (found/absent/content)
- every lead: `string, source_file, verify_result, verdict`
- every dead lead: the same + the falsifier that fired
- the adjacent-disclosure probes
- the `solved_via` if a lead closed the challenge
- the `reopen_if` precondition

## The field-notes.md growth

`../field-notes.md` grows every time this class's recon contributed to a
solve — record the exact lead (source file + verbatim string) that led
to the finding and the class that closed it. When a map-led solve
lands, the class earns `verified` — the card records which signal
surfaced the winning lead.

## The honest-vs-verified note

This class is catalogue — record leads as "the map produced X" not
"the map was the exploit". The chain card belongs to the class that
closed it (`web-idor`/`web-auth-session`); `web-source-map`'s role is
recorded as the recon that surfaced the lead.
