# Class boundary — race-condition vs the confusable classes

The line between `web-race-condition` and the classes it shares signals with —
chiefly `web-logic-flaw`, plus the classes a race *feeds*.

---

## 1. The core boundary — temporal vs spatial

| | race-condition | logic-flaw |
|---|---|---|
| the bug is | temporal — a gap between check and act | spatial — the check itself is wrong |
| needs | concurrency / overlap | a single request |
| proof | a serial-impossible state | a wrong-state result on one request |
| example | `if (balance>=amt) withdraw()` raced | `if (balance>=0) withdraw(-100)` serial |

The confusable is `web-logic-flaw` — the SKILL.md says so. If your "win"
reproduces *serially*, it's a logic flaw, not a race: reclassify.

```bash
# the discriminating probe — does it work with NO concurrency?
curl -s -X POST "$BASE/api/withdraw" -d '{"amount":-100}' -b "$SESSION"
# a negative amount accepted serially → logic flaw, not a race
```

## 2. Race-condition vs web-logic-flaw — the detailed split

| Signal | Class |
|---|---|
| the check is correct, the gap lies | race-condition |
| the check is wrong or missing | web-logic-flaw |
| needs `max_in_flight ≥ 2` | race-condition |
| works on a single request | web-logic-flaw |
| "balance>=amt then withdraw" | race (gap) or logic (no check) — probe serial |
| "buy with price=0 in the body" | web-logic-flaw / mass-assignment |
| "redeem the same code twice, fast" | race-condition |
| "redeem a code that isn't yours, once" | web-idor |

## 3. Race-condition vs web-idor

| | race | idor |
|---|---|---|
| the object access | a *timing* problem — two actors on one resource | an *authorization* problem — you accessed an object not yours |
| example | two users race one seat | you read `/api/order/123` that isn't yours |

A race can *produce* an IDOR-shaped outcome (your row where theirs should be),
but the mechanism is the timing — classify by the mechanism.

## 4. Race-condition vs the classes it feeds

A race is a *primitive provider* — the flag is usually reached through a
different class's sink:

| Race produces | The sink class |
|---|---|
| a stored field under your control | `web-xss` / `web-ssti` (ApexSurvive) |
| an owned account | `web-csrf` / `web-auth-session` (SSOS) |
| money / credits | `web-logic-flaw` / `web-idor` (buy the gate) |
| a token in your mailbox | `web-auth-session` |
| a stale-view privilege | `web-auth-session` / `idor` |
| a second live session | `web-auth-session` |

Classify the *primitive* as `web-race-condition`; the *sink* is the class that
carries the flag — record both, chain them in the card.

## 5. Race-condition vs web-request-smuggling

| | race | request smuggling |
|---|---|---|
| the mechanism | two requests, same record, a timing gap | two parsers disagree on where a request ends |
| the signal | `max_in_flight` + crossed state | desync — a request "leaks" into another's response |

A request-smuggling desync can *cause* a race (a smuggled second request lands
inside a window) — but the smuggle is the transport, the race is the record
conflict. Confusable but distinct.

## 6. The shared-signal table

| Signal | Race | Confusable |
|---|---|---|
| "two requests interfere" | race | smuggling (parser), logic (check) |
| "a check passes that shouldn't" | race (gap) | logic-flaw (wrong check), idor (no check) |
| "a limit is exceeded" | race (counter) | logic-flaw (no limit code) |
| "a token delivered wrong" | race (cross) | host-header (address confusion) |
| "duplicate record" | race (uniqueness) | logic-flaw (no dedup) |
| "state changed unexpectedly" | race | csrf (a forged request), stored-xss |

## 7. The decision probe — is this a race?

```bash
# 1. does it need concurrency? race_probe --baseline-count 5 --count 0 --no-barrier
#    if the "win" appears serially → NOT a race → logic-flaw / idor
# 2. does it need overlap? --concurrency N → max_in_flight ≥ 2 produces what serial can't
#    if max_in_flight = 1 produces nothing → still a race (mechanics), re-roll
# 3. does it need a shared record? a request-local value can't race
```

## 8. When to reclassify

| Observation | Reclassify to |
|---|---|
| works serially, no overlap needed | `web-logic-flaw` |
| a check that never runs | `web-idor` / `web-auth-session` |
| the "race" is a smuggled request | `web-request-smuggling` |
| the sink is an XSS/CSRF | race is the primitive; the sink class gets the flag |
| a price/quantity you control in the body | `web-mass-assignment` / `web-logic-flaw` |
