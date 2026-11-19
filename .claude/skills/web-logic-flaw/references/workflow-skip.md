# Workflow skip — the step order is assumed, not enforced

The workflow assumes step N ran before step N+1 — but the API does not
enforce the order. Each endpoint trusts the sequence; nothing checks the
state that sequence was supposed to produce.

## The mechanism

```
intended:  POST /cart → POST /checkout → POST /payment → POST /confirm
skipped:   POST /confirm          (directly — no cart, no payment)
```

The endpoint trusts the pipeline: "if you're calling `/confirm`, you must
have paid." Nothing re-checks. The skip is the flaw.

## The detection

### Map the workflow

```bash
# walk the intended flow once — record every step and what it produces
curl -i -b "$JAR" -L "$BASE/buy" 2>&1 | tee flow.txt

# extract the endpoint sequence from the responses
grep -oE '(action|href|url|endpoint)="[^"]+"' flow.txt
grep -oE 'POST [^ ]+|GET [^ ]+' flow.txt
```

The workflow is the ordered endpoint list. Each step produces something the
next step consumes — a token, a state flag, a session attribute, a row.

### The trust signals

- An endpoint takes an `id`/`token`/`state` produced by an earlier step —
  does it verify, or trust?
- A multi-step form with `step=1`, `step=2`, `step=3` parameters — does
  `step=3` require steps 1-2 completed?
- A checkout/payment/confirm sequence — does `/confirm` check the payment
  actually succeeded, or just that it's called?
- A register → verify-email → activate sequence — can you activate without
  verifying?
- A challenge → solve → flag sequence — can you fetch the flag without
  solving?

## The probe

```bash
# skip to the last step directly
curl -i -b "$JAR" -X POST "$BASE/confirm" -d 'orderId=1'

# or skip the middle step — start, jump to end
curl -i -b "$JAR" -X POST "$BASE/checkout" -d 'step=3&cartId=1'

# or call the terminal endpoint with a fabricated upstream token
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'token=FORGED_STATE'
```

## The confirmation

The later step accepts — the terminal action runs without the precondition:

```
HTTP/1.1 200 OK
{"status": "confirmed", "orderId": 1, "charged": 0}
```

The `charged: 0` — the order is confirmed without payment. The state the
rules forbid is reached: a confirmed unpaid order, a flag without a solve,
an activated unverified account.

## The falsifier

The endpoint checks the precondition state — the response names the missing
step:

```
HTTP/1.1 400 Bad Request
{"error": "payment required before confirm"}
```

or the endpoint re-runs the check itself and fails:

```
HTTP/1.1 402 Payment Required
{"error": "no successful payment for order 1"}
```

## The workflow shapes

| Shape | The skipped step | The payoff |
|---|---|---|
| checkout skip | payment | free goods — order confirmed unpaid |
| verification skip | email/phone verify | active unverified account |
| password-reset skip | token validation | set a new password without the token |
| challenge skip | the solve step | the flag without the solve |
| kyc/onboarding skip | the document step | privileged account without KYC |
| 2fa skip | the second factor | login without the OTP |
| captcha skip | the challenge | automated action without captcha |
| consent skip | the approval step | action without user consent |
| review skip | the approval step | publish without review |
| step N+1 of M | any middle step | the terminal state directly |

## The evidence rules

- A `200` on the terminal endpoint is not alone a confirmation — the state
  must be the forbidden one. Read the object back: is the order confirmed
  AND unpaid? Is the account active AND unverified?
- The upstream artifact is the evidence: the `orderId` that was never paid,
  the `token` that was never issued.
- A `302` to an earlier step is a negative — the workflow enforced the
  order, record it.

## The traps

- **A `200` that produces no forbidden state is inconclusive.** The endpoint
  may have run and produced nothing — read the state back.
- **The token may be signed.** A fabricated upstream token may fail
  signature verification — the flaw is then "predictable token", not
  "workflow skip". Classify accordingly.
- **Steps may be enforced on the client only.** The JS may gate step 3
  behind step 2's success, but the server may not — test the server, not
  the client.
- **Parallel endpoints may both write.** Calling `/confirm` while
  `/payment` is in flight is a race — see `web-race-condition` — not a
  workflow skip.
