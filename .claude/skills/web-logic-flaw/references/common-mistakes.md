# Common mistakes — the ways business-logic testing goes wrong

## Mistake 1 — mutating payload spellings instead of changing layers

Sending `role`, `isAdmin`, `is_admin`, `admin`, `userRole`, `user_role`,
`accessLevel`, `privileges` — eight probes of the SAME mechanism against a
proven allowlist. Once `role=admin → role:user` is measured, the allowlist
is proven; every spelling variant is the same dead probe. The Polynomial
lesson: hundreds of variants inside one class with nobody stopping it.
`decide.py` exists to stop exactly this — five probes per class, then the
layer changes, not the spelling.

## Mistake 2 — calling a `200` a confirm

Registration succeeded → "mass assignment confirmed". No — registration
succeeds for ordinary users too. The forbidden state (`role: admin`) must
appear in a **read-back** response. Until then it's a candidate.

## Mistake 3 — trusting the write echo

`POST /register {"role":"admin"}` returns `{"role":"admin"}`. That echo
proves the server *parsed* the field — not that it *stored* it. Read the
object back through a separate GET. Many frameworks echo the request body
while binding only allowlisted fields.

## Mistake 4 — two variables in one probe

`quantity=-1&coupon=SAVE50` returns a negative total. Which caused it?
Unknowable — and unrecordable as class evidence. One probe, one changed
variable, always.

## Mistake 5 — no baseline

`balance: 200` after a replay means nothing without the `balance: 150`
after the first redeem and the `balance: 100` before it. Logic evidence is
a *diff*, not a value. Baseline first, always — the same discipline as
`race_probe`'s serial baseline.

## Mistake 6 — trusting the UI's bounds

The form caps `quantity` at 10 → the tester never sends 11. The UI bound
is a client suggestion; the server bound is measured from rejection
behavior. Pachinko again: the accepted ID range was mapped from server
rejections, not the UI — the UI's limit and the checker's limit were
different numbers.

## Mistake 7 — assuming the documented check is the real check

The docs say "node IDs must be < 100". The checker bounds the raw index.
The write uses `off + id*S`. The documented limit and the enforced limit
and the *effective* limit are three different numbers — measure all three.

## Mistake 8 — treating a chain card as proof

`chain_match` returns the Pachinko card → "this is a validator gap". No —
the card is a candidate shape. Its `first_confirming_probe` runs against
THIS target; a literal signal match is a lead, a `family_leads` hit is a
card to READ. Neither is a finding.

## Mistake 9 — skipping the falsifier

The probe list grows, the falsifier never runs. Every hypothesis ships
with its kill shot — run it EARLY. A falsifier firing in probe 2 saves
probes 3–5 for another layer.

## Mistake 10 — burying negatives

"Didn't work" probes go unrecorded, so the next session re-walks them.
Every probe writes to the ledger — confirm, falsified, or negative — with
the `--response` attached.

## Mistake 11 — testing the happy path for state

Checking `/order/1` after skipping payment — but `/order/1` shows
`status: confirmed` from a PREVIOUS test. Isolate state: fresh object per
probe, or a read-back baseline proving the state wasn't already there.

## Mistake 12 — stopping at the first layer's boundary

Pachinko's deepest trap: the transport layer (what IDs are accepted) and
the checker layer (what IDs the checker intends) and the address layer
(where the write lands) are three different bounds. Confirming "ID 4096
is rejected" at the transport says nothing about where `off + id*S`
lands. Keep asking *which* layer rejected.
