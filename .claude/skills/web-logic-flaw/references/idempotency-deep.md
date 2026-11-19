# Idempotency deep — the exactly-once machinery

`state-replay-deep.md` covers the marker mechanics. This module is the
full idempotency landscape — where "exactly once" must hold, where it
actually holds, and the coverage probes.

## What needs idempotency

Any transition whose second application changes state further:

- `redeem`/`claim` — double-credit;
- `refund` — double-refund;
- `transfer`/`withdraw`/`deposit` — double-apply;
- `vote`/`like`/`invite` — double-count;
- `reset`/`verify` links — double-consume (a replayed reset token is a
  session hijack path);
- `confirm`/`fulfill` — double-fulfillment.

## Where it's implemented

| Layer | Shape | Coverage question |
|---|---|---|
| endpoint check | `if (seen(key)) return 409` | which key? which scope? |
| ledger/dedup store | `INSERT ... ON CONFLICT DO NOTHING` | what's the conflict column? |
| DB unique constraint | `UNIQUE(code, user)` | column coverage |
| idempotency-key header | `Idempotency-Key` middleware | body-hash covered? |
| nowhere | — | the serial shape |

## The coverage probes

```
probe 1: A,A identical → 409?              endpoint-level marker exists
probe 2: same key, mutated body → ?        first-write-wins vs body-hash
probe 3: key under user2 → ?               per-user vs global key scope
probe 4: action via /claim vs /redeem → ?  per-endpoint vs shared store
probe 5: redeem→refund→redeem → ?          compensation clears marker?
probe 6: key=K1 then key=K2 same body → ?  is key client-chosen?
```

Each row answers a coverage question — `409` means that scope is
covered; `200`+effect means it's open.

## `Idempotency-Key` semantics

The IETF pattern: middleware stores `(key → response)`; a replay with
the same key returns the STORED response. The gaps:

- **no body-hash**: same key + different body → does the store return
  the first response (first-write-wins — the mutated body never
  applied) or apply the second (the key is a label, not a contract)?
- **TTL**: keys expire — replay after expiry.
- **scope**: key stored per-user → cross-user replay.
- **coverage**: `Idempotency-Key` honored on `/redeem`, ignored on
  `/refund` — the middleware is per-route.

## The evidence

```
before:  {"balance": 100}
after1:  {"balance": 150, "requestId": "r1"}
replay:  same requestId, same body → {"balance": 150}  (dedup'd) OR
         {"balance": 200}  (double-applied)
```

Dedup'd means the response returns the FIRST result — verbatim `150`
without applying. Double-applied is the confirm.

## The atomicity question (boundary with race)

`if (!seen) { apply(); mark_seen(); }` — serial replays see the marker;
parallel requests both pass `!seen` before either marks. Serial `409`
closes THIS class's question; the parallel window belongs to
`web-race-condition` — `race_probe --write-ack`, serial baseline first.
