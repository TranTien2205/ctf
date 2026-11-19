# Per-mechanism index — the cross-reference table

One row per mechanism — module, probe, falsifier, evidence, the
adjacent class it routes to.

| Mechanism | Module | Probe | Falsifier | Evidence | Routes to |
|---|---|---|---|---|---|
| mass assignment | `mass-assignment.md` | register+field → read-back | `role:user` / `400` | stored privileged field | web-mass-assignment |
| workflow skip | `workflow-skip.md` | terminal step bare | `302/400` earlier step | terminal + missing precondition | — |
| state replay | `state-replay.md` | action ×2 serial | `409` | effect doubled verbatim | web-race-condition |
| numeric boundary | `numeric-boundary.md` | boundary alphabet | `400`/clamp | forbidden arithmetic state | — |
| scaling-after-check | `two-validator-gap.md` | `id` past limit vs malformed | identical rejection | different-layer rejection | — |
| unit confusion | `mechanism-alphabet.md` | value in other unit | canonical normalization | wrong-scale charge | — |
| role assignment | `role-assignment.md` | privileged field at create | allowlist | stored role + gated reach | web-mass-assignment |
| idempotency | `state-replay.md` | exact replay same key | `409` | key covered, effect once | web-race-condition |
| time assumption | `mechanism-alphabet.md` | past/future values | `400` on invalid | expired-forbidden accepted | — |
| sequence | `mechanism-alphabet.md` | stale ID replay | `409` | stale state restored | — |
| ownership | `mechanism-alphabet.md` | foreign objectId transition | `403` | transition on foreign object | web-idor |
| singleton | `mechanism-alphabet.md` | second privileged create | `409` | second privileged object | — |
| trust-in-earlier-step | `trust-in-earlier-step.md` | mutate upstream value | `400 mismatch` | minted≠accepted verbatim | — |

## Detection table

| Mechanism | Black-box signal | White-box signal |
|---|---|---|
| mass assignment | model fields > form fields in GET | `create(req.body)`, `**req.json` |
| workflow skip | multi-step flow, `step` carriers | handler `pre()` missing predicate |
| state replay | one-time artifacts — codes/tokens | no consumed-marker |
| numeric boundary | arithmetic fields | `!= 0` checks, unchecked `qty*price` |
| scaling-after-check | index fields, different-layer rejections | `id<LIMIT` + `mem[off+id*S]` |
| unit confusion | implicit-unit fields | conversion multiply/divide |
| idempotency | `Idempotency-Key`, one-time actions | no check-and-set |
| time | expiry/notBefore/timestamp in reach | client-read time fields |
| sequence | monotonic IDs | no ordering check |
| ownership | objectId in operations | missing owner check on path |
| singleton | "the" privileged object | no unique constraint |
| trust | hidden fields, echoed minted values | `req.body.total` trusted |

## The sweep order

```
cheapest first (1 GET):   terminal endpoints bare
1 POST + 1 GET:           mass assignment, workflow skip, replay
alphabet per field:       numeric boundary (5-8 rows/field)
computed probes:          transform wrap, unit, trust
```

Total sweep cost: ~30-50 requests — inside the challenge budget with
room for the chain walk.
