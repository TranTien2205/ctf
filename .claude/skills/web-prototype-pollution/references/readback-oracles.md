# Readback oracles — how you know the pollution landed

The write and the observation are always two requests. `pp_probe.py
--readback` exists because a `200` on the update means nothing until a
second fetch shows the marker somewhere it shouldn't be.

---

## 1. The marker contract

A marker must be:

- a property name the app never sets (`ppmarker`, `training_marker`,
  `x_probe_9f`) — not `admin`/`role`/`debug` (those could come from
  another code path),
- a value that's distinguishable (`"pp-1408"` with a nonce),
- readable on an object you did not write (a fresh object, another
  route's response, a different user's doc).

`pp_probe` uses a generated marker per run for exactly this reason —
a colliding property name makes the readback ambiguous.

## 2. The oracle ranking

| Oracle | What it proves | Weight |
|---|---|---|
| marker on a FRESH object (new note/user/doc) | global write | proof |
| marker on an unrelated endpoint's JSON | global write | proof |
| marker reachable via `{}.marker` in an admin console | global | proof |
| a fallback-behaviour change (403→200, render shows marker) | the sink READ it | proof of payoff |
| marker on the SAME object you wrote | local write — NOT the class | ambiguous |
| marker never seen | write failed or merge shallow | negative |
| a 500/error mentioning `__proto__` | setter path attempted | lead |

## 3. Where to read back

The readback URL options, cheapest first:

```
GET /api/me              — your own object (local-write control)
GET /api/items           — a list (fresh objects materialize)
GET /api/items/<new>     — a brand-new object
GET /api/settings        — the settings object itself
GET /                    — any page rendering a fresh {}
GET /api/status /health  — trivial JSON renders
POST /api/items (create) — the new object's response
```

The freshest object is the best readback — a newly created doc has
no reason to carry your marker unless it inherited it.

## 4. The `readback-changed` signal

`pp_probe`'s subtler verdict: no marker in the body, but the response
DIFFERS — status changed, length changed, a header appeared, a field
type changed. The prototype got the property; the serializer dropped
it or the sink consumed it. A 403→200 on a gated route after
`{"__proto__":{"isAdmin":true}}` is `readback-changed` — the gate
read the fallback.

## 5. The timing oracle

When nothing textual changes:

- Pollute `__proto__.sleep = 3000` (or a `timeout` field a sink reads)
  — a sink that awaits `opts.timeout` on the NEXT request delays it.
- Pollute a property that hits a `console.log`/`debug` path — the log
  line (if you can read it) or the extra ms of the I/O.
- Pollute `__proto__.heavyComputation = true` where a route branches
  on it — the route's latency shifts.

Timing oracles are last-resort — a 50ms delta on one request is
noise; need ~20 samples per arm.

## 6. The error oracle

The merge/setter throws on a bad write:

- `{"__proto__": "string"}` — assigning a primitive to `__proto__`
  can throw `TypeError: Immutable prototype object` or silently set
  the proto to the primitive — the 500 vs silent split reveals the
  engine's behaviour.
- `{"__proto__": {"m": {}}}` where a later sink expects `m` a string
  — the sink's type-error proves it READ `m`.
- `{"__proto__": {"m": Symbol}}` / unparseable value — parse-stage
  rejection tells you the key reached the parser at least.

## 7. The multi-object readback

The cleanest confirm sequence:

```bash
# 1. write the marker via A's session on A's own object
POST /api/settings {"__proto__":{"ppm":"v1"}}
# 2. read a fresh object as A
GET /api/fresh → {"ppm":"v1",...}   → global write confirmed
# 3. read as B (second session) — does B's objects carry it?
GET /api/fresh (as B) → {"ppm":"v1",...} → process-global
```

Step 3 is the blast-radius measurement — pollution on the shared
`Object.prototype` hits every requester's objects, which is why
marker properties must be meaningless.

## 8. The `no readback` case

Some merges never echo — a write to a store that only surfaces via
a later computed field. The alternatives:

- **The behaviour readback**: the sink's effect IS the observation
  (a 403 opens, a render includes the flag, a process runs).
- **A second read path**: the same object through a different route
  (`/items/<id>` vs `/api/v2/items/<id>` vs `/export`).
- **The websocket/event feed**: an event payload echoing the merged
  state.

No observable readback = `inconclusive`, not `refutes` — the write
may have landed where you can't see. Record it as such; move to a
sink whose effect IS observable rather than claiming a miss.
