# Environment matrix — what survives restart, worker, serverless

Whether a pollution write persists, and where it lands, depends on
the deployment model — the write's blast radius AND its lifetime
are both environment properties.

---

## 1. The process model — who shares the prototype

```
single-process app        → PP pollutes the one process — every
                            request of every user inherits it
multi-process (cluster)   → pollutes only the worker that handled
                            the write — hit-or-miss on which
                            worker serves the readback request
multi-container           → pollutes only the container — an L7
                            load-balance may route the readback
                            elsewhere
per-request worker (CGI)  → pollution dies with the request —
                            only second-order (stored) writes
                            survive
serverless (per-invoke)   → same — cold-starts reset; warm-invoke
                            reuse may persist across invocations
threaded (Python)         → the class/globals write is shared
                            across threads — pollution is global
                            within the process
worker_threads (Node)     → each thread has its OWN isolate —
                            pollution stays in the writing thread
child_process fork        → each child its own process — write
                            lands in the child only
```

## 2. The persistence boundary

| Write lands in | Survives restart? | Survives worker-recycle? |
|---|---|---|
| process memory (Object.prototype) | no | no |
| a class object (Python) | no | no |
| `__globals__` dict | no | no |
| `os.environ` | no | no |
| the merge TARGET object | no (unless persisted) | no |
| a stored JSON blob (DB/file) | yes | yes |
| a serialized session | yes (session life) | yes |
| a written file (`/tmp/x`) | yes | yes |
| a config on disk | yes | yes |
| a spawned child's env | child-life | child-life |

**In-memory pollution is per-process and per-lifetime** — the
readback must happen in the same process and before a restart.
That's why the marker-probe pairs the write and the readback
back-to-back: the window is the process lifetime, not the session.

## 3. The cluster/worker wrinkle

```js
// node cluster — each worker its own process + proto
// the write hits worker W1; the readback hits W2 → clean-looking!
// falsifier-trap: a real PP write reads as refuted because the
// readback routed to a different worker
```

Detection: send the same write+readback pair N times — a hit-rate
of `1/workerCount` indicates a real write whose oracle only fires
on the polluted worker. A `Server`/`X-Worker`/`x-powered-by`/
pid-leaking response can confirm multi-process.

```bash
for i in $(seq 1 20); do
  curl -s -X POST "$BASE/update" -d '{"__proto__":{"ppmarker":"v1"}}'
  curl -s "$BASE/fresh" | grep -o ppmarker
done | sort | uniq -c    # ~1/N hit-rate → multi-worker
```

## 4. The serverless/warm-invoke case

```text
cold-start → handler → return → (worker killed or reused)
warm-reuse → handler (same process!) → return
```

A warm AWS-Lambda/GCF/Cloudflare-worker reuse keeps the process —
a pollution write persists across invocations on warm hits. The
readback must land on a warm invoke of the SAME container — not
guaranteed; same hit-rate test applies.

## 5. The per-request worker (CGI-style)

A CGI/uwsgi-per-request model forks per request — memory writes
evaporate at request end. Only a write to SHARED state persists:

- a stored JSON blob re-merged per request (the profile shape)
- a file the worker writes
- a shared cache key
- a database field

The second-order shapes (`second-order.md`) are the ONLY carriers
that work here — first-order in-memory PP is impossible.

## 6. The Python threading case

Python apps run threads within ONE process — `setattr` on a class
or `__globals__` write is process-global across threads — the
readback fires on any thread. But GIL means the write+read are
serialized — timing windows are wider.

## 7. The Node worker_threads / child_process case

```js
new Worker(...)              // separate isolate — own proto
fork(modulePath)             // separate process — own proto
cluster.fork()               // separate process
```

A pollution write in the MAIN thread doesn't reach workers or
forks — BUT a polluted option (env/execArgv/workerData) read at
spawn-time DOES carry into the child — the spawn-time read is the
transfer.

## 8. The readback-window table

| Deployment | Write→read window | Strategy |
|---|---|---|
| single-proc | process lifetime | immediate readback |
| cluster | same worker only | N-try hit-rate or sticky session |
| multi-container | same container | sticky session or N-try |
| serverless-warm | warm-container lifetime | hit-rate; store in /tmp for durability |
| per-request CGI | none (in-memory) | second-order only |
| threaded-py | process lifetime | immediate |
| worker_threads | same thread | the spawn-time option read |
| forked child | child lifetime | workerData/env/options at spawn |

## 9. The stickiness trick — cookies/IPs for worker affinity

```bash
# if the LB routes by cookie, keep the session cookie constant
# across write+readback so both land on the same worker
curl -c cj -b cj -X POST "$BASE/update" -d '{"__proto__":{"m":"v1"}}'
curl -c cj -b cj "$BASE/fresh"     # same cookie → same worker
```

When the app sets a session/affinity cookie, reuse it — the LB's
affinity routes both requests to the same backend.

## 10. The "pollution survived restart" cases

- the write was to a STORED object (profile/settings blob) — the
  pollution is IN THE DATA, re-merged on each load
- the write dropped a file (`/tmp/x.js`) a later `require` picks up
- the write set a config on disk read at startup
- the write was in a spawned child's env read back on next spawn
- a cache key was poisoned with a polluted-context result

## 11. The ledger note

```bash
python3 tools/state.py <c> --hypothesis "env: single-proc in-memory pp" \
  --decision "readback must pair write in same request-window"
```
