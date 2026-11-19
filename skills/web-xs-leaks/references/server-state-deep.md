# Server-state deep — the mutation channels, exhaustively

Every server-state oracle — a mutation the GET caused that you read back.

---

## 1. The LRU-eviction channel — the recency read

```text
a redis --maxmemory-policy allkeys-lru — every write can evict the
least-recently-used key. a GET that touches a key REFRESHES it —
marks it recently-used. flood the store to force eviction → the
surviving keys are the recently-touched ones — the bot's GETs —
the SURVIVOR SET is the leak.
```

```text
the bandwidth: a store with K keys carries K bits per visit — a
thousand-bit channel — the whole char-set or a whole secret's
markers in ONE visit.

the blast_radius: the flood evicts EVERY other key — possibly the
secret itself — only flood an instance that's yours alone.
```

## 2. The counter channel — the next-value read

```text
a GET that increments a counter you can read — 'the counter is N+1
after the bot's visit' → the bot's GET ran → the candidate matched.
```

```bash
# the counter surface
redis.incr('counter')
# or an app-level counter — a page-views, a visit-count
```

```text
the bandwidth: a few bits per visit — the counter's value is the
leak — 'how many GETs ran'.
```

## 3. The one-shot-token channel — the single-use flag

```text
a GETDEL/single-use nonce — 'did the token survive the bot's visit'
is one bit AND burns the check — a spent token is gone.
```

```bash
# a GETDEL surface
redis.getdel(token)     # get-then-delete — 'did it survive'
```

```text
the spend-order: spend the one-shot LAST — the cheaper channels
(a counter, a recency, a CSS oracle) narrow the answer first — the
one-shot's one bit is spent on the LAST narrowing.
```

## 4. The rate-limit channel — the quota read

```text
a bucket with a remaining count — a consumed quota = 'the GET ran' —
the remaining quota is the leak.
```

```bash
# a rate-limit surface — a remaining count
# 'X-RateLimit-Remaining: N' — the consumed quota
```

## 5. The 'last seen' channel — the recency timestamp

```text
a timestamp a GET updates — 'the last-seen time is T' → 'the GET
ran at T' — a recency read.
```

## 6. The session-mutation channel — a GET's side-effect

```text
a GET that mutates a session — a stored value, a flag, a state —
'the session's value is X after the bot's visit' → the GET ran.
```

## 7. The write-back channel — an airgapped exfil

```text
an airgapped bot — a write-back (a POST to the target storing the
leaked data — a comment, a field) — the data lands on the TARGET —
you read it back later — no external listener needed.
```

```bash
# a write-back surface — a comment/note endpoint
curl -X POST "$BASE/api/comment" -d '{"text":"<leaked>"}'
# the data lands on the target — read it back via a GET
curl "$BASE/api/comments" | grep '<leaked>'
```

## 8. The DOM-writeback channel — a screenshotting bot

```text
a bot that SCREENSHOTS the page — a DOM-writeback (the secret
rendered visibly in a large font) — the screenshot IS the exfil —
no listener, no server-state read needed.
```

```js
// a DOM-writeback — the secret rendered visibly
document.body.innerHTML='<div style="position:fixed;inset:0;background:#fff;font-size:80px">'+leaked+'</div>'
```

## 9. The per-channel bandwidth — the visit-count question

```text
an LRU-eviction     — thousands of bits — a single visit
a counter           — a few bits — a few visits
a one-shot token    — one bit — one visit (spend last)
a rate-limit bucket — a few bits — a few visits
a 'last seen'       — a recency read — one visit
a session-mutation  — a few bits — a few visits
a write-back        — the whole secret — one visit
a DOM-writeback     — the whole secret — one visit (a screenshot)
```

## 10. The per-channel requirement — what each needs

```text
an LRU-eviction     — a redis --maxmemory-policy allkeys-lru + a
                      flood that fits the rps
a counter           — a readable next value
a one-shot token    — a GETDEL/single-use surface
a rate-limit bucket — a remaining count
a 'last seen'       — a timestamp a GET updates
a session-mutation  — a GET that mutates a readable session
a write-back        — a POST endpoint that stores the data
a DOM-writeback     — a bot that screenshots the page
```

## 11. The channel's read-back — how you read the mutation

```text
a counter           — a GET /counter — the current value
a rate-limit        — a header — 'X-RateLimit-Remaining'
a 'last seen'       — a GET /last-seen — the timestamp
a session-mutation  — a GET /session — the stored value
a write-back        — a GET /comments — the stored text
an LRU-eviction     — a SCAN of the store — the surviving keys
```

## 12. The channel's blast-radius — the destructive question

```text
an LRU-eviction     — the flood evicts EVERY other key — possibly
                      the secret — a shared-store flood is a
                      destructive channel
a counter           — a harmless increment — non-destructive
a one-shot token    — a spent token is gone — a burned check, not a
                      destructive channel
a write-back        — a stored comment — a small write
a DOM-writeback     — a DOM mutation — non-destructive
```
