# Common questions deep — the exhaustive race FAQ

Every race-condition question that comes up, with the probe or the record that
answers it. Long-form companion to `common-questions.md`.

---

## Reproduction and evidence

### Is a race real if I can only sometimes reproduce it?

Yes — a race is probabilistic by definition. The class is proven by a single
serial-impossible outcome attributed to a named pair, not a 100% hit rate.
Reliability is an engineering problem solved by widening the window or
tightening delivery, not a correctness question.

### How many requests do I need — two or a flood?

Two, correctly interleaved. The goal is landing a second commit inside a
named window — a flood hides which pair crossed and unattributable success is
not evidence. `race_probe --concurrency N` is the burst form for a wide
window; the interleave (`--url-b` / a stall) for a narrow one.

### What's the difference between a burst and an interleave?

A burst fires N complete requests at once — it wins when the window is wide
enough that one commits while others are mid-read. An interleave holds
request A open (a withheld last byte) while B completes — it lands B inside
A's already-open window. Narrow windows need the interleave.

### How do I know the requests actually overlapped?

`race_probe` reports `max_in_flight` — the peak requests in flight at once.
`1` = serialized (inconclusive). `≥ 2` = real overlap. Never interpret a
`max_in_flight=1` run as a negative or a positive.

### The endpoint returns 200 to everything — did I win?

Only if the *state* changed impossibly. Two `200`s where serial produces one
`200` + `409` is the race; two `200`s where serial also produces two `200`s
is a replay. Read the state — the balance, the inventory — not the status.

### A timeout during the race — does it count?

No — a timed-out slot produced no readable response; its contribution is
unknown. Discard it and re-roll. A timeout is never a success or a falsifier.

### The second `200` has an identical body — did it double the effect?

Check the state. An identical `200` body with no doubled effect is a response
cache or a polite dedup — a falsifier, not a win.

### A `500`/`IntegrityError` on the loser — win or crash?

A falsifier — the constraint caught the loser. `23505`/`1062`/`duplicate key`
is the defence doing its job, never a second success.

## Architecture and scope

### The app wraps everything in a transaction — is the race closed?

No — a transaction is not a lock. At READ COMMITTED (the default) the `SELECT`
reads a snapshot and both transactions write. The window closes only with
`FOR UPDATE`, an atomic `UPDATE ... WHERE`, a constraint, or SERIALIZABLE.

### The server has one worker — can I race it?

Not at the HTTP layer — requests serialize at the accept queue. Race the
layer below: two replicas on a shared DB, a background worker's claim, or the
app issuing two queries that interleave at the DB.

### Is a race on a shared instance allowed?

Only on an object you own. A race corrupts the raced record — a negative
balance on the shared demo account corrupts it for every player. Race your
own account/code, and confirm a one-shot target is fresh first.

### The race needs a different account — same session or two?

Two sessions. Racing one session against itself hits the per-account dedup;
the resource is global but the check is per-account — race two actors on the
global resource behind a shared barrier.

### The race won once but not again — real or noise?

Real — probabilistic. Re-roll (with `--reset-url` to restore state) until you
can attribute the pair. If it won once the window exists; if you can't
re-roll, the delivery or the reset is the problem.

## Mechanism and classification

### How is a race different from a logic flaw on the same endpoint?

A race is temporal — the check is correct, the gap between check and act
lies. A logic flaw is spatial — the check itself is wrong, no timing needed.
`if (balance>=amt) withdraw()` races; `if (balance>=0) withdraw(-100)` is a
logic flaw that works serially. Classify before probing.

### Is a negative balance a real crossed state or a display bug?

A real crossed state — the serial floor is 0; `balance = -amt` cannot be
produced serially. The balance column value, read back from `/api/account`,
is the evidence.

### When is "two of the same 200" actually the win?

When the serial baseline proves one `200` then declines, *and* the raced run
produces two `200`s under real overlap, *and* the state shows the doubled
effect. All three — the split, the baseline, and the state — are the
attribution.

### Can a race happen across a multi-step flow?

Yes — the "transaction" is a session record shared across steps. A `cart/add`
landing between `checkout`'s compute and `pay`'s charge is the widest form —
`--url-b` the two steps.

### The race is on a queue/worker — how do I probe it?

Race two trigger requests, or a trigger against the worker's claim —
`SELECT pending → UPDATE running` is the window. `SKIP LOCKED` is the close;
its absence is the window.

## Delivery and technique

### The rate limiter blocks the burst — is the endpoint safe?

No — the limiter gates how many requests reach the handler; it doesn't close
the handler's window. Race the limiter (it's a counter), or stay under it
with a tighter interleave.

### The window is too narrow for the burst — now what?

Widen the check: a pathological input that makes validation do more work — a
catastrophic-regex email, a long uniqueness field, a deeply-nested object.
The PhantomFeed technique — the timing delta between a normal and a
pathological input is the signal that a widening primitive exists.

### When do I use `--url-b` vs a manual stall?

`--url-b` for two *different* complete requests (a token-cross, a flow race,
read-vs-write). A manual raw-socket stall for a single request held
*mid-request* — withhold the last body byte, complete B, release A — the
ApexSurvive mechanic.

### HTTP/2 vs HTTP/1.1 — does the delivery change?

On h2 the requests are frames — withhold each stream's last DATA frame, flush
all at once (the h2 stall / single-packet). `race_probe`'s barrier does the
TCP-level equivalent. One-request-per-connection matters more on h1
(multiplexing can serialize).

### What does `--signature-mode` do and which do I pick?

It tells the tool how to split win from loss:

- `status` — win/loss differ in status (200 vs 409)
- `status-length` — status same, body length differs
- `raw-body` — a second token/cookie in the body
- `normalized-body` — strip timestamps/ids
- `regex` + `--signature-regex` — pull the distinguishing field
- `--signature-header NAME` — a header (Set-Cookie, Location)
- `--signature-bytes N` — only the first N bytes

## Recording and escalation

### What goes into the evidence record?

The baseline split, the raced split, `max_in_flight`, the state read, and the
attributed pair — with the verbatim excerpt inside `--response` for
`post-probe`.

### When is "no cross" a falsifier vs inconclusive?

A falsifier requires real overlap — `max_in_flight` ≥ 2 across clean rolls
with the defence holding. An `inconclusive` (`max_in_flight` = 1) run proved
nothing — fix delivery and re-roll.

### What do I do when the budget is spent?

`decide.py` answers `escalate` — the cheapest untried rung in order:
`chain_match` → `reclassify` → `writeup_search` → `novel_plan` →
`fanout_sweep` → `solver_handoff`. Record each with
`state.py --strategy-used`.
