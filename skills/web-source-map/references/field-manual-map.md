# Field manual map — the operator sequence as a visual

## The pipeline

```
ENTRY PAGE
    │
    ├─> script inventory ................ M1
    ├─> manifest (build/asset/sw) ........ M2
    │
    ▼
EVERY BUNDLE
    │
    ├─> map probe (4 routes) ............. M4
    │     │
    │     ├─> .map found? ─┬─ yes ─> reconstruct ──> M5 source
    │     │                │                         │
    │     │                └─ no ──> string mine      ├─> M7 layout
    │     │                          (M6,M8,M10)      ├─> M9 comments
    │     │                                           └─> M10 sinks
    │     │
    ├─> string mine .................... M6 endpoints
    │                                    M7 params
    │                                    M8 secrets
    │                                    M9 flags
    │                                    M10 config
    │
    ▼
LEAD LIST (endpoints, secrets, params,
           routes, flags, hosts, sources)
    │
    ├─> TRIAGE .......................... M15 rank
    │
    ▼
VERIFY EACH LEAD ...................... M16 live check
    │
    ├─> live ──> ROUTE to its class ...... M17
    ├─> dead ──> record negative
    └─> unverifiable ──> route to a reach class
    │
    ▼
ADJACENT (if .map / lax deployment) ... M18 .git/.env/backups
```

## The stage table

| Stage | Mechanism | Command | Output |
|---|---|---|---|
| inventory | M1/M2 | `curl` + manifest probes | the bundle set |
| map | M4 | `curl .map`/header/inline | a real map? |
| mine | M5-M14 | `bundle_miner` + greps | the lead list |
| triage | M15 | rank by value | the ordered leads |
| verify | M16 | `curl`/`Authorization`/`pre-flag` | live/dead per lead |
| route | M17 | class per lead | the routed findings |
| adjacent | M18 | `.git`/`.env` probes | the bigger leak |

## The per-stage stop

- inventory done → every chunk + lazy route enumerated
- map done → every map route probed per bundle
- mine done → `bundle_miner` + targeted greps ran
- verify done → every lead has a live result
- route done → every live lead routed, every dead lead recorded
- the pass done → every lead is verified-or-dead

## The one-line mental model

**inventory → map → mine → verify → route** — the map names the
surface; the verify decides what is real; the class exploits it.
