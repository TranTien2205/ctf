# Anti-patterns — the probe shapes that never produce evidence

A catalogue of request patterns that LOOK like business-logic probing
but produce no attributable signal — each with the correction.

## The unprompted spray

Sending `role`, `isAdmin`, `admin`, `is_admin`, `userRole`,
`accessLevel`, `privileges`, `superuser`, `staff`, `moderator` in one
loop — ten requests, zero attributable results, one proven falsifier
re-proven nine times.

**Correction**: one field → read-back → falsifier or confirm → NEXT
MECHANISM. The allowlist answers all spellings at once.

## The dual-variable probe

`quantity=-1&coupon=SAVE50` — the negative total could come from
either. Unrecordable as class evidence: `--evidence` can't name which
variable caused it.

**Correction**: each leg alone first, then the composition — three
attributable results.

## The baseline-less claim

`balance: 200` → "replay worked". No `before`/`after1` rows — the 200
could predate your probes entirely.

**Correction**: the three-read series — before, after1, after2 — all
recorded.

## The echo confirm

`POST` returns `{"role":"admin"}` → declared confirmed. The echo proves
parsing, not storage.

**Correction**: separate GET read-back — the echo/store diff IS the
evidence.

## The stale-state read

Skip `/confirm`, GET `/order/1` shows `confirmed` — from a previous
test.

**Correction**: fresh object per probe, or a baseline field
(`createdAt`, `sequence`) proving the state is new.

## The UI-bound respect

"The form caps qty at 10" → never sends 11. The UI bound is fiction;
the server bound is measured.

**Correction**: send past the UI bound; binary-search the rejection.

## The doc-bound respect

"IDs must be < 100" → never sends 101. Docs describe the imagined
check; the transform's reach is a different number.

**Correction**: send it — the Pachinko lesson: the accepted range is
mapped from rejection behavior, not documentation.

## The identical-negative loop

50 malformed-circuit variants, 50 identical rejections — every probe
hit the same layer. The card's verbatim lesson.

**Correction**: identical rejections = the layer is mapped → change
LAYER (field, carrier, endpoint), not payload.

## The 500-as-confirm

A `500` on `id=abc` declared "the transform gap". A `500` is a crash —
which layer crashed needs the contrast probe before it means anything.

**Correction**: `id=<limit+1>` vs `id=abc` — compare the shapes; the
DIFFERENCE is the signal.

## The 429-as-rejection

Rate-limited responses counted as falsifiers. `429` is a budget fact,
not a layer answer.

**Correction**: exclude `429`s from the rejection map; space the
probes.

## The card-as-proof

`chain_match` returns Pachinko → "validator gap confirmed". The card is
a candidate shape; its `first_confirming_probe` hasn't run on this
target yet.

**Correction**: run the card's probe verbatim; a `family_leads` hit is
a card to READ — never a probe to run.
