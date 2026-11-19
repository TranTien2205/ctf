# Negative results (deep) — the full dead-end ledger

## Why the ledger matters

Bundle recon is cheap to redo wrongly — a solver re-mines the same
bundle hoping the strings changed. They do not. Recording the negative
*with the measurement* stops the re-walk.

## The ledger schema

```json
{
  "layer": "web-source-map",
  "challenge": "<name>",
  "bundles_mined": ["main.js", "2.chunk.js", "page-admin.js"],
  "map": {"probed": ["main.js.map", "2.chunk.js.map"], "found": false},
  "sources_recovered": 0,
  "leads": [
    {"string": "/api/internal", "result": "404", "verdict": "dead client route"},
    {"string": "apiKey candidate", "result": "fails auth", "verdict": "dead"},
    {"string": "feature.admin", "result": "server-enforced", "verdict": "dead"}
  ],
  "verdict": "negative — bundle mined, no actionable lead",
  "reopen_if": "the deployment ships a new bundle or a .map"
}
```

## The per-lead negative record

Every lead that fails its falsifier gets a row:

| Lead | Source file | Falsifier result | Verdict |
|---|---|---|---|
| `/api/internal` | `main.js:1` | `curl` → 404 | dead client route |
| `apiKey` candidate | `config.js:3` | auth check → 401 | dead key |
| `feature.admin` | `app.js:412` | flag set → same 403 | server-enforced |
| `/admin` | `routes.js:9` | `/api/admin` → 404 | client-only path |

A dead lead without its source file is not traceable — record the file
it came from.

## The depth-4 negative

The most valuable negative: leads existed but *none verified*. Record it
explicitly — "the map produced N leads, all dead" — because it is the
difference between "the bundle was thin" and "the bundle was mined and
the surface is genuinely public".

## The reopen condition

A negative has a precondition that reopens it — a new deployment, a
`.map` appearing, a different environment bundle (`main.dev.js`). Record
`reopen_if` so the negative is a measurement, not a permanent verdict.

## The handoff

The negative ledger hands the next layer its dead ends — do not re-mine
the same bundle; the next recon surface is `.git`/`.env`/backups or a
`web-triage` signal, not a second pass.
