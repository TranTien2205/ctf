# Case studies — the canonical race-condition engagements

Each case names the target shape, the window, the delivery, and the lesson.
The two verified cards are in `verified-chains.md`; these are the reusable
patterns and real-world shapes the class produces.

---

## Case 1 — The double-spend coupon (the canonical CTF race)

```text
target:    POST /api/coupon {code} → grant points if !used
window:    SELECT used → grant → UPDATE used=1 (no constraint, no tx)
delivery:  burst — the window is ms-scale
result:    two grants for one code — 2× the points
```

- **Probe**: `race_probe --url $BASE/api/coupon --body '{"code":"WELCOME"}' --concurrency 20 --count 20 --baseline-count 5 --write-ack`
- **Crossed state**: baseline `[200,400,400,400]`, raced `[200,200,400,...]`;
  `GET /api/points` shows 2× the coupon value.
- **Lesson**: the most common shape — a single-use code with a code-level
  `if !used` and no DB backing. The whole exploit is landing two requests in
  the read→write gap.

## Case 2 — The bank-overdraw (Turbo Intruder's classic)

```text
target:    POST /api/transfer {amount} → if balance>=amt: debit
window:    SELECT balance → if → UPDATE balance
delivery:  single-packet burst of N transfers for the full balance
result:    N× the balance extracted; balance = -(N-1)×amt
```

- **Probe**: `--body '{"amount":100}' --concurrency 10 --count 10`
- **Crossed state**: 10 accepted transfers of the full 100 balance; the
  account reads `-900`.
- **Lesson**: the double-spend's money form. The `balance >= amt` check and
  the `balance - amt` write being separate statements is the entire bug.

## Case 3 — The profile-token cross (ApexSurvive's primitive)

```text
target:    POST /profile {email} → mint token → commit → re-read → sendEmail
window:    mint and send not atomic — an interleaved commit lands between
delivery:  interleave — withhold A's last byte, drop B inside, release A
result:    token minted for a@x delivered to mailbox b@y — which you read
```

- **Probe**: two interleaved profile updates (a@x, b@y); observe which mailbox
  gets whose token. Needs the stall, not a burst.
- **Crossed state**: the token for address A arrives at address B.
- **Lesson**: the widest-window races are the ones with *work between* the
  read and the re-read — `sendEmail` is the giveaway. The burst can't win a
  narrow window; the interleave can.

## Case 4 — The registration race against a bot (SSOS's primitive)

```text
target:    a bot's startup registers student@domain; the endpoint is check-then-insert
window:    SELECT email → INSERT
delivery:  hammer /register before the bot's startup reaches registerUser
result:    you own the account the bot thinks it owns — the confused deputy
```

- **Probe**: `for i in seq: curl -X POST /register -d '{"email":"student@domain","password":"yours"}' &`
- **Crossed state**: your password logs into the bot's account.
- **Lesson**: race the *identity* the actor will claim, not a random resource.
  The bot then does privileged work on your account — the highest-value race
  primitive.

## Case 5 — The single-packet limit bypass

```text
target:    POST /api/vote → if count<1: insert
window:    SELECT count → INSERT
delivery:  HTTP/2 single-packet — all last DATA frames in one write
result:    2 votes from one account
```

- **Probe**: `race_probe --concurrency 20 --count 20 --baseline-count 4`
  (the tool's barrier is the single-packet mechanic).
- **Crossed state**: score +2 for one voter.
- **Lesson**: when the window is tight, the delivery mechanic is the
  differentiator — single-packet is the tightest start barrier available.

## Case 6 — The timing-oracle window discovery (PhantomFeed)

```text
target:    an endpoint whose check is a catastrophic regex on a field
window:    normal input ms, pathological input ×10 slower — the window widens
delivery:  the pathological input IS the widen — then a normal race
result:    the timing delta proves a widen exists; the race then lands
```

- **Probe**: `curl -w '%{time_total}'` on a normal vs a `a@`+26chars+`!` input
  — the delta is the window.
- **Lesson**: the race doesn't always need a faster client — it can need a
  *slower check*. A pathological input buys the window.

## Case 7 — The multi-step cart race

```text
target:    cart → checkout (computes total) → pay (charges the total)
window:    the total is computed at checkout, charged at pay — a record between
delivery:  POST /cart/add {expensive} racing POST /pay
result:    the charge is for the pre-add total — the new item is free
```

- **Probe**: `--url-b` — `pay` as A, `cart/add` as B.
- **Lesson**: the widest windows are the *multi-request* ones — the
  "transaction" is a session record shared across steps.

## Case 8 — The job-queue double-execute

```text
target:    worker claims: SELECT pending → UPDATE running → execute
window:    no FOR UPDATE SKIP LOCKED — two workers claim the same job
delivery:  two workers racing the claim, or two trigger requests
result:    the job runs twice — two emails, two charges
```

- **Probe**: `--url-b` two trigger requests, or race a request against the
  worker's poll.
- **Lesson**: the queue's claim is a check-then-act too — `SKIP LOCKED` is the
  close; its absence is the window.

## Case 9 — The OTP attempt-cap race

```text
target:    POST /verify {code} → if attempts<5: check; attempts++
window:    SELECT attempts → if<5 → UPDATE attempts+1 → compare code
delivery:  burst N > cap wrong guesses
result:    all N answered "invalid" not "locked" — the cap never engaged
```

- **Probe**: `--concurrency 20 --count 20` on a cap-5 endpoint.
- **Crossed state**: more than 5 attempts processed.
- **Lesson**: a counter race doesn't bypass the check — it buys *more tries*.
  Combine with a short/weak OTP for the brute-force window.

## Case 10 — The stale-read privilege ride

```text
target:    GET /api/me reads verified → a privileged route trusts the view
window:    the GET's snapshot vs the POST /revoke that just committed
delivery:  --url-b GET /api/me + POST /api/revoke
result:    the GET returns verified:true *after* the revoke committed
```

- **Probe**: `--url-b` the read against the write.
- **Lesson**: not every race is a double-write — a stale *read* trusted past
  its validity is the read-only TOCTOU.

## The case → alphabet → lesson table

| Case | Alphabet | The one-line lesson |
|---|---|---|
| coupon | C | a code-level `if !used` with no constraint is the whole bug |
| bank | B | `balance>=` check and `-` write in two statements |
| profile | E | work (`sendEmail`) between mint and re-read is the window |
| register | A | race the identity a system actor will claim |
| vote | D | tight window → single-packet delivery |
| timing | (oracle) | a slower check buys the window |
| cart | multi-step | the session record is the shared state |
| queue | Q | `SKIP LOCKED` absence is the window |
| otp | L | a counter race buys more attempts, not the answer |
| stale-read | V | a trusted stale view is the read-only TOCTOU |
