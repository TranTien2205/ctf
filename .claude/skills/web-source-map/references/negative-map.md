# Negative map — every dead end and its record

## The dead-end taxonomy

| Dead end | What fired | Record |
|---|---|---|
| no bundle | entry loads no app `.js` | `no SPA -> not this route` |
| no map | `.map` 404/`text/html` everywhere | `no map -> string mine only` |
| map no content | `sourcesContent` null | `file names only -> structure leads` |
| opaque strings | no endpoints/secrets/flags in the bundle | `bundle opaque -> no leads` |
| dead endpoint | 404 / catch-all | `dead client route` |
| dead secret | fails auth / publishable | `dead/publishable key` |
| server-enforced flag | `403` regardless | `server-side gate -> dead lead` |
| client-only route | `/api/x` 404s | `client route, not a server path` |
| traversal | `sources` escapes `--out` | `rejected traversal -> hostile map` |
| all leads dead | every falsifier fired | `mined, nothing actionable` |

## The record shape

```json
{
  "layer": "web-source-map",
  "bundles_mined": ["main.js", "2.chunk.js"],
  "map": "404 on all guesses",
  "sources_recovered": 0,
  "leads": [
    {"string": "/api/internal", "src": "main.js", "result": "404", "verdict": "dead client route"},
    {"string": "apiKey candidate", "src": "config.js", "result": "401", "verdict": "dead key"}
  ],
  "verdict": "negative — mined, no actionable lead",
  "reopen_if": "the deployment ships a .map or a dev bundle"
}
```

## The per-lead dead-end record

Each dead lead: `string, source_file, falsifier_fired, result`. A dead
lead without its source file is not traceable.

## The clean-negative value

A clean "mined, nothing actionable" is the *most* valuable negative —
it proves the surface is public-only, closing the route for the next
solver. It is a measurement, not a failure.

## The reopen-if rule

Every negative carries its `reopen_if` — the precondition that would
reopen it. A `.map` appearing, a dev bundle, a different role, a new
deployment — the negative is a measurement with an expiry, not a
permanent verdict.

## The handoff

The negative ledger hands the next layer its dead ends — do not re-mine
the same bundle; the next recon surface is `.git`/`.env`/`web-triage`,
not a second pass.
