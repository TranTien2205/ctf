# Real-world cases — business-logic patterns from production incidents

Catalogue knowledge — documented industry shapes, not solves from this
repository. They exist to widen the mechanism alphabet with patterns
that recur in CTF design.

## The negative-quantity refund

An e-commerce flow: `quantity` field in the cart accepted negative
integers; checkout computed `total = Σ qty·price`; a `-50` total was
processed as a refund-to-card. The pattern: **arithmetic trusted a
sign the workflow never produces**. The CTF version ships the same
check `qty != 0` instead of `qty > 0` — probe the sign before the
magnitude.

## The price-parameter carry

A checkout flow rendered `price` into a hidden form field at the
product page and trusted it at order submission. The fix was "server
recomputes"; the bug was trust-in-earlier-step. The CTF version: a
`data-price` attribute, a JSON `total` echo, or a cart API returning
`subtotal` that `/checkout` accepts back verbatim.

## The coupon stack

A discount field accepted a coupon code array; each element applied
independently — `["SAVE10","SAVE10","SAVE10"]` stacked triple-discount.
The pattern: **the one-time check applied per-element, not per-
request**. Probe `[code]` vs `code`, and duplicate elements inside the
array.

## The transfer-to-self

A `transfer` endpoint debited `from` and credited `to` — both
client-supplied. `from == to` netted zero in the ledger but the
"available balance" check read the pre-debit balance, letting the
debit pass. The pattern: **the check and the effect read different
states of the same value**. In CTF: `from=me&to=me` first, then
`from=victim&to=me` (the ownership version).

## The parallel-withdrawal

Serial replays were deduped; parallel withdrawals raced the balance
check — N requests, all saw `balance >= amount`, all posted. The
pattern: **idempotency without atomicity**. That's the boundary with
`web-race-condition` — serial falsifier first, parallel probe second.

## The role-in-claims pattern

A registration bound `role` from the body; later the same app moved
role into a signed JWT claim and the register binder stayed permissive
— an account registered with `role=admin` kept a server-side role the
JWT never re-derived. The lesson: **where the privilege is STORED
decides which endpoint can write it** — the binder at object creation
vs the claim at token mint are different write paths.

## The step-parameter trust

A multi-step onboarding carried `step` in the POST body; `step=5` on a
fresh session completed the flow with all intermediate defaults —
`verified=false` but `account=active`. The pattern: **the step index
IS the state machine**, and it's client-writable. Probe the terminal
step value on a fresh session.

## The enum-out-of-range

A `type` field enum `{free, pro}`; `type=2`/`type=-1`/`type=enterprise`
fell through the `if type==free elif type==pro` chain into a
`default:` that granted admin-tier. The pattern: **enum checks that
don't exhaust**. Probe out-of-enum values — integer indexes past the
list, unlisted strings, and `null`.

## The batch-endpoint duplicate

An API accepted `{"ops": [...]}` batches; the same `redeem` op twice in
one batch both applied — the dedup ran per-request, not per-element.
The pattern: **batching bypasses per-request uniqueness**. Probe
`ops=[A,A]`, `items=[A,A]`, and alias-based GraphQL duplications.

## Cross-pattern

Every case is the four-invariant frame: field conservation (role in
body), ordering (step param), uniqueness (replay/stack/batch), value
integrity (sign, price carry, transform). Production bugs and CTF
challenges share the alphabet — the catalogue differs only in how the
sink expresses impact.
