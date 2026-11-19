# Multi-step chains — the canonical race-into-flag compositions

The race is the primitive provider. These are the reusable compositions —
each names the race primitive, the pivot it buys, and the sink class that
carries the flag.

---

## 1. Race → money → gated purchase → flag

```text
race POST /withdraw (double-withdraw)     → balance = 2× or negative
buy the gated item (the flag/endpoint)    → the purchase check passes
read the item / receipt / endpoint        → the flag
```

| Rung | Probe | Signal |
|---|---|---|
| the race | `race_probe` on `/withdraw` amount=full | balance `-amt` |
| the purchase | `POST /buy {flag_item}` after the race | 200 where 403 before |
| the flag | `GET /order/:id` / the item | flag string in response |

Chain-card hook: none yet — this is the most common composition; the money
primitive almost always pays for a gate.

## 2. Race → token-cross → account primitive → stored XSS → bot → flag

```text
race POST /profile (token→wrong mailbox)  → own the change
store a template-literal XSS in a field   → admin bot renders it
bot's session → file-write / privileged   → template-overwrite RCE
```

The ApexSurvive card — the full chain is in `verified-chains.md` §1. The race
only matters because it hands you a rendered field the bot trusts.

## 3. Race → owned-identity → confused-deputy → flag-in-your-mailbox

```text
race POST /register for the bot's account → you own it
the bot's later steps run on your account → cookie-swap CSRF binds it
the bot submits the flag at startup        → read as the author
```

The SSOS card — `verified-chains.md` §2. Race the *identity* the actor will
claim, not a random resource.

## 4. Race → uniqueness → confused-deputy → data plant

```text
race /register → two rows with one username (no UNIQUE)
the SSO/import/lookup maps to *your* row   → privileged data written to you
```

A generalization of SSOS: race a uniqueness check against a *system* actor's
account, not just a bot.

## 5. Race → double-grant → threshold → flag

```text
race /vote or /claim (double-accept)      → count = 2× cap
a threshold gate ("top voter", "N claims") → crossed
the reward / leaderboard / unlock          → the flag
```

Used where the flag is behind a quantity gate, not a purchase — race to
exceed it.

## 6. Race → OTP-attempt-cap → brute-force window → account

```text
race /verify-otp (attempts > cap)         → N concurrent wrong guesses pass the count
the probability window opens               → enough attempts to land the code
the session / account                      → the flag path
```

This is a *probability* exploit, not a bypass — the race doesn't guess the
code, it buys the guesses. Combine with a weak/short OTP.

## 7. Race → stale-read → trusted-view → privilege

```text
race GET /api/me against POST /revoke      → GET returns verified:true post-revoke
the app trusts the stale view              → a privileged act rides it
```

The read-only TOCTOU — no double-write, just a snapshot trusted past its
validity.

## 8. Race → file-creation → overwrite → content-injection

```text
race POST /upload same filename (2 saves)  → path/ownership confused
the second save writes over the first      → your content where theirs was
the file is rendered/served                → stored content
```

`exists()` → `save()` TOCTOU over HTTP; the winner's file lands where the
loser's check pointed.

## 9. Race → session-issue → persistent/confused session

```text
race /login (one-session policy)          → 2 live sessions
the second session survives a "logout-all" → a persistent or deputy session
```

Buys a session that outlives a rotation or a policy that assumed one.

## 10. Race → queue-job → double-execute → second effect

```text
race the job trigger / the worker's claim → the same job runs twice
two sends / two charges / two writes       → the doubled side-effect
```

`SELECT pending` → `UPDATE running` without `SKIP LOCKED` — two workers, one
job.

## 11. Race → cart/checkout → price-confusion → free/cheap item

```text
race POST /cart/add against POST /pay      → pay reads a total computed before the add
the charge is for the old total            → the new item is free, or the order is wrong
the order / receipt                        → the flag path
```

The multi-request-flow boundary — the "transaction" is the cart record shared
across steps.

## 12. Race → token-rotation → replayable old token

```text
race POST /token/refresh (2 interleaved)   → the old token stays valid
replay the superseded token                → a session that shouldn't exist
```

The invalidate ran before the other request's store — the "dead" token lives.

## The composition table

| # | Race primitive | Pivot | Sink class |
|---|---|---|---|
| 1 | double-withdraw | money | `web-logic-flaw`/`idor` |
| 2 | token-cross | account → stored field | `web-xss` → file-write → `web-ssti` |
| 3 | owned-identity | confused deputy | `web-csrf` → read submission |
| 4 | uniqueness | system-actor mapping | `web-auth-session` |
| 5 | double-grant | threshold gate | `web-logic-flaw` |
| 6 | attempt-cap | probability window | `web-auth-session` |
| 7 | stale-read | trusted view | `web-auth-session`/`idor` |
| 8 | file-creation | overwrite | `web-file-upload`/stored |
| 9 | session-issue | persistent session | `web-auth-session` |
| 10 | job-double | second effect | `web-logic-flaw` |
| 11 | cart/pay | price confusion | `web-logic-flaw` |
| 12 | token-rotation | replay | `web-auth-session` |
