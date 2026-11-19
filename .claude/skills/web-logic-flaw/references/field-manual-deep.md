# Field manual deep — the business-logic engagement, every branch rendered

`field-manual.md` is the straight walk. This module is the same
engagement with every decision tree expanded — what each response
opens next.

## The opening position

```bash
python3 selfcheck.py
python3 tools/state.py <name> --category web --target <url> \
  --challenge-name "<real>" --event "<event>"
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --record <name>
```

If `chain_match` returns the Pachinko card — or any card whose `chain[]`
prose mentions "bounds check", "transform", "offset", "scale", "wrap" —
its `first_confirming_probe` runs verbatim first. A `family_leads` hit
is a card to READ, not a probe to run.

## Decision tree: the register endpoint

```
POST /register + role=admin → read-back
├── role:admin   → CONFIRM class → enumerate role-gated surface → flag
├── role:user    → falsifier (flat, this endpoint)
│   ├── try PATCH/PUT same model (different binder) — 1 probe
│   ├── try nested {"user":{"role":"admin"}} — 1 probe
│   ├── try form content-type — 1 probe
│   └── all falsified → mass assignment dead at model level → next mechanism
└── 400          → strict schema → try other content-types → dead → next
```

## Decision tree: the workflow

```
call terminal step bare (/confirm, /flag, /activate)
├── 200 + forbidden state   → CONFIRM → read the terminal's flag field
├── 302/400 to earlier step → state enforced → WHERE?
│   ├── cookie: forge step=N directly
│   ├── param/body: send step=N in the transition call
│   ├── server session: try the TERMINAL endpoint bare — it may not
│   │   participate in the state machine at all
│   └── parallel session: share objectId across two sessions
└── 200 + unchanged state   → soft no-op → negative, record the layer
```

## Decision tree: the numeric fields

```
per field (quantity → price → discount → tax → amount):
  send boundary alphabet rows
  ├── 400 all rows       → field validated → NEXT FIELD
  ├── clamped            → silent bound → note layer → NEXT FIELD
  ├── accepted + forbidden state → CONFIRM → checkout test
  └── 500/crash          → unguarded transform → CONFIRM different-layer
```

## Decision tree: the one-time action

```
redeem ×2 serially
├── +effect twice  → CONFIRM no-marker
├── 409 second     → falsifier endpoint-level → probe key scope:
│   ├── same key + mutated body
│   ├── cross-user
│   └── parallel (route to race if serial dead)
└── 200 twice, effect once → ledger-level dedup → probe the ledger
    key's coverage (requestId? endpoint? object?)
```

## Decision tree: the transform

```
id=<doc limit>  → baseline accept
id=<limit+1>    → compare vs id=<malformed>
├── different rejection → transform unchecked → CONFIRM gap →
│   compute wrap: id such that off + id*S mod 2^w → target
└── identical rejection → falsifier → transform checked/absent
```

## The chain assembly

Each CONFIRM opens edges. The flag reach table:

| Confirmed state | Where the flag usually is |
|---|---|
| `role:admin` | field inside `/admin*` views, `/export` |
| `balance:+N` | flag item priced above legit max |
| `confirmed+unpaid` | flag field in the terminal order |
| `skip → verified` | gated endpoint behind verification |
| `transform write` | code overwrite → privileged op |

## The closing position

```bash
python3 tools/hooks.py pre-flag <name> --value "<flag>" \
  --source "GET /flag response" --evidence "<flag>"
python3 tools/classify_solve.py --chain <id>
```

Or, alphabet spent: `python3 tools/decide.py <name>` — the next rung
(`writeup_search`, `novel_plan`, `fanout_sweep`), never a sixth
spelling. Kill map → `knowledge/attempts/<name>.json` when the session
ends unsolved.
