---
name: web-race-condition
description: Prove a race with the serial control that makes it a race. Use when a limit, a counter, a one-shot token or a state transition is checked and then written — choosing the window, the single-packet and parallel-connection bursts, measuring that the serial baseline really is impossible, and the cleanup a successful race owes.
classes: race-condition
---

# Race conditions

Proof requirement: **an outcome impossible under serial execution, with the
serial control recorded.** Three checks — two distinct actors or orderings, a
control for the expected outcome, outcomes that actually differ.

The control is not paperwork around the finding; it *is* the finding. From the
outside a flaky endpoint and a race are one observation: a request that usually
fails and sometimes succeeds. What separates them is a serial run that never does.

## Choosing the window: the gap between a check and its write

| shape | the check | what two concurrent requests get you |
|---|---|---|
| read-check-write on a counter | balance, stock, quota, remaining uses | the limit overrun by one |
| uniqueness | "this email is taken" | two accounts on one identity |
| one-shot token | coupon, gift card, reset token, invite | it redeemed twice |
| state machine | order is `pending`, so cancel is allowed | cancelled *and* shipped |

Prefer the endpoint whose response reports the remaining count: the window is
then measurable rather than inferred, and one request tells you the precondition
is still set up. Two concurrent requests against a limit of one is the whole
proof; forty is a load test, and availability work is refused here.

## The serial control is the measurement

`http.differential` with `repeat=3` comes first, before any concurrency: it issues
each side three times, compares the first baseline against the last, and when the
page differs from itself it says so — *this differential proves nothing*. At the
default `repeat=1` nothing is compared and `baseline_stable` comes back true
anyway, so that silence means nothing: a page's own noise is the race you misread.

Then run the request serially, N times, with the precondition reset exactly as
the race will see it. "Twenty serial attempts, nineteen refused with 409" is what
makes a parallel success impossible rather than lucky, and N is the point: one
success in twenty parallel attempts with no serial run is a 5% event with no
denominator, and rate limiting, a proxy retry, an idempotency key and plain load
all produce it. The class budget is six probes, so twenty attempts cannot be
twenty `http.probe` calls: one loop, one control record.

## The burst: two mechanisms, and the target chooses

- **Single-packet (HTTP/2 or HTTP/3).** Hold 20–30 requests multiplexed on one
  connection, withhold the final frame of each, release them in one TCP packet.
  Jitter between connections stops being a variable, which is how you reach a
  sub-millisecond window. Use it whenever HTTP/2 is negotiated end to end.
- **Parallel connections with a last-byte sync (HTTP/1.1).** Open N connections,
  send all but each request's final byte, let them settle, release the last bytes
  together. Weaker: the spread between the connections is the floor on the window.

`http.probe` and `http.differential` issue one request at a time. Unless a burst
tool is registered (`knowledge.playbook` names this class's tools) the burst runs
outside the broker on threads over a barrier, returning through
`ledger.add_evidence` and graded on the same terms. But outside it nothing calls
`pre_probe` — no scope, tier or budget check, no refusal recorded — so check the
origin against the engagement's scope yourself, and prefer a registered tool.

## Recording it so the matrix can grade it

```
ledger.add_evidence kind=probe vuln_class=race-condition hypothesis_id=hy-...
  record={"ordering":"parallel-20","target":"https://t/api/coupon/redeem",
          "extracted":{"sent":20,"accepted":3,"state_after":"credit applied 3x"},
          "response":{"status":200,"body_span":"<a success body>"}}

ledger.add_evidence kind=control vuln_class=race-condition hypothesis_id=hy-...
  record={"ordering":"serial-20","is_control":true,
          "extracted":{"sent":20,"accepted":1,"refused":19},
          "response":{"status":409,"body_span":"coupon already redeemed"}}
```

- `ordering` is what satisfies "two distinct actors or orderings" — two records
  both labelled `parallel` fail that check. Two identities instead of two
  orderings passes too, which is the shape when the race is between accounts.
- `kind=control` is the second check, and `is_control` is not an argument of the
  tool: pass it inside `record` or the call returns `bad-arguments`.
- "outcomes actually differ" is read from `response.status`, so the records must
  carry the statuses that differ: the burst's success and the serial refusal.

**If the application answers 200 to both the accepted and the refused request,
that third check cannot pass** and the grade stops at `supported` with "outcomes
actually differ" named. Do not relabel the control's status to get past it:
record the state read that shows the overrun and let the report say the outcome
differs in the body. A candidate with the gap named beats an argued `proven`.

## Cleanup, because a race creates records

A working race leaves artifacts: duplicate orders, extra credit, two accounts on
one identity, a coupon redeemed three times. Three obligations, as for a stored
payload — record what it created, by id, as its own evidence record; reverse what
can be reversed and record that; say in the report what is left behind. Never
re-run a proven race: each repetition is another row in somebody's database.

## What does not count

- **A burst with no serial control.** The class cannot be graded, correctly.
- **An intermittent 500 under concurrency.** Evidence about error handling. A
  race is an *outcome* the business logic forbids, not a stack trace.
- **Two successes where two were allowed.** Read the limit first: "remaining: 2"
  makes the second success correct behaviour.
- **A duplicate created by your own retry.** Your client, a proxy or a
  double-submitted form will do this; the burst must be the only sender.
- **Source code that looks unsafe.** A read-check-write with no lock is a good
  hypothesis and a strong report line; the outcome is still the requirement.
