# Extended corpus — the broad race-condition reference set

The wide-net module: less-common shapes, exotic windows, and the long tail of
races that don't fit the canonical playbook.

---

## 1. The long-tail endpoint shapes

| Endpoint | The race | The crossed state |
|---|---|---|
| `POST /api/cancel-order` racing `POST /api/ship` | cancel vs ship on one order | a shipped order also marked cancelled |
| `POST /api/refund` racing `POST /api/charge` | refund vs charge | both applied — net wrong |
| `POST /api/bid` racing `POST /api/bid` | two bids on one auction | the "winner" is ambiguous, or bid-history corrupt |
| `POST /api/apply` racing `POST /api/approve` | apply vs approve | an approved application never submitted |
| `POST /api/enroll` racing `POST /api/drop` | enroll vs drop on a full course | over-cap enrollment |
| `POST /api/follow` racing `POST /api/follow` | duplicate follow | count +2, one relationship |
| `POST /api/share` racing `POST /api/share` | a one-share reward | two rewards |
| `POST /api/report` racing `POST /api/report` | a report-once flag | two reports / a duplicated trigger |
| `POST /api/export` racing a data change | export snapshot vs update | an export that's half old half new |
| `POST /api/delete` racing `POST /api/read` | delete vs read | a read on a deleted object that still returns |

## 2. The exotic-window shapes

### The DNS/TLB-style race (resolve-then-connect)

```text
gethostbyname(host) → check it's not internal → connect(host) → DNS rebinds
```

A check that resolves a hostname, then a connect that re-resolves — a DNS
rebind between them lands on a different IP. The TOCTOU is the two resolutions.

### The certificate/verification race

```text
POST /verify-domain → check DNS TXT → mark verified → an attacker flips the TXT
```

The check reads a record the attacker controls; the "verified" flag persists
after the record changes.

### The lock-expiry race (redlock-style)

```text
acquire lock with TTL → do work that exceeds TTL → the lock expired mid-work
```

A distributed lock that expires *during* the protected section — a second
actor acquires it while the first still believes it holds.

### The optimistic-UI race

```text
client disables the button after click → the second click already in flight
```

The "defence" is client-side — two requests both carry the pre-disable state.

### The token-bucket timing race

```text
consume a token at T → the bucket refills → consume again before the refill is checked
```

A rate-limit token bucket where the consume and the refill-check race.

## 3. The second-order races

A race whose crossed state only pays *later* — the effect is dormant until a
separate trigger.

| Shape | The dormancy |
|---|---|
| race a uniqueness check on a field that becomes a key later | the lookup that uses it resolves to you |
| race a flag/counter that a periodic job reads | the job's next tick applies the doubled value |
| race a relationship (follow/ownership) that's resolved lazily | the deferred resolve maps to your row |
| race a cache that outlives a rotation | the stale entry serves post-rotation |

## 4. The multi-resource joint races

The invariant is across *several* resources — write-skew's generalization.

| Shape | The joint invariant |
|---|---|
| team cap across member rows | "team.members < cap" — decrement two different rows |
| pooled balance across accounts | "A+B >= withdrawal" — debit both |
| shared quota across tenants | "sum(usage) < quota" — use both |
| parent-child count | "parent.children == actual" — insert two children |

`FOR UPDATE` on each row doesn't close it — the invariant is across rows.
Needs SERIALIZABLE or a group lock.

## 5. The signal/callback races over HTTP

The "second request" is an event, not a request.

| Shape | The event |
|---|---|
| a webhook that re-enters the handler | fire the webhook mid-request |
| a completion callback racing the initiator | the callback commits first |
| a websocket message racing an HTTP write | two channels, one record |
| a scheduled task firing mid-request | the task's write vs the request's |

## 6. The read-only races (no double-write)

Not all races write — a race on a *view* or a *snapshot* is exploitable.

| Shape | The crossed state |
|---|---|
| a GET racing a POST revoke | verified:true post-revoke |
| a cached read racing an invalidate | pre-write value post-commit |
| a replica read racing a primary write | a lagged "truth" |
| a report/export racing an update | a report of a half-state |

## 7. The probability-window races

The race buys *tries*, not the answer.

| Shape | What it buys |
|---|---|
| OTP attempt-cap | more guesses than the cap |
| a one-shot guess endpoint | several guesses in one window |
| a "first N get it" contest | your request in the first N |
| a random-draw prize | more entries than allowed |

## 8. The persistence-window races

The race buys a state that outlives its intended scope.

| Shape | What persists |
|---|---|
| session-issue race | a second session past a "one session" policy |
| rotation race | a superseded token that stays valid |
| cache race | a poisoned/stale entry that outlives the fix |
| a "temporary" grant race | a grant that was meant to expire but the consume raced |

## 9. The corpus → alphabet index

| Extended shape | Alphabet row | Detail |
|---|---|---|
| cancel-vs-ship | M/W | `per-route.md` |
| refund-vs-charge | M | `per-check-balance.md` §1 |
| bid | D-like | `per-check-balance.md` §3 |
| enroll/drop | J/H | `check-then-act-alphabet.md` |
| follow/share/report | C/G/R | `per-check-balance.md` §2 |
| export-vs-update | read-only | `per-mechanism.md` §7 |
| DNS-rebind | path TOCTOU | `per-mechanism.md` §4 |
| cert-verify | V | `check-then-act-alphabet.md` |
| lock-expiry | concurrency primitive | `per-surface.md` §6 |
| optimistic-UI | client-side | `edge-cases.md` |
| token-bucket | L | `check-then-act-alphabet.md` |
| second-order | (deferred) | this file §3 |
| multi-resource | write-skew | `per-mechanism.md` §8 |
| signal/callback | event | `per-mechanism.md` §6 |
| read-only | view | `per-mechanism.md` §7 |
| probability | L | `check-then-act-alphabet.md` |
| persistence | S/token | `per-check-token.md` §4 |
