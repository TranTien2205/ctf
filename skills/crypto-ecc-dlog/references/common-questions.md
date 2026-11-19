# Common questions — the FAQ the corpus answers

## "I have two signatures — is that enough?"

If the `r` values match → `ecdsa-nonce-reuse`, one command, done.
If `r` differs → only if `k` is bounded/biased → `hnp-ecdsa`. One
signature alone: nothing works.

## "Do I need the order?"

Yes — `--order` is `n` (the subgroup order), not `p`. On named curves it's
published; on custom curves the handout usually gives it. `smoothness` and
`bsgs`/`pohlig-hellman` all read it.

## "What format does `--sigs` want?"

A JSON **file** (not inline) — a list of `[r, s, z]` triples or
`{"r","s","z"}` objects, ints or hex strings.

## "What's `z`?"

`int(hash(message))` — truncated to `order_bits` (FIPS 186-4) by default;
`mod n` is the alternative if the verify fails.

## "The lattice is slow — why?"

`lll.py` is pure-python (no `fpylll` here). Keep signature count near
`required_signatures`; the matrix is `m+1` dimensional.

## "The recovered `d` looks plausible but doesn't verify"

Then it's wrong — `z`, `order`, bound, or the attack itself. A scalar that
doesn't reproduce the public key is not the key.

## "Curve params given but no `n` — what now?"

Count `#E` if `p` small (`ec.py`), else check for defect-curve intent
(anomalous/singular). If `#E == p` → `smart_attack`; `Δ == 0` →
`singular_ec`.

## "`h = g^x mod p` but `p` is huge"

`smoothness --n p-1` — if the largest factor is small, `pohlig-hellman`;
if `x` bounded, `bsgs`. A safe-prime `p` means the bug is elsewhere.
