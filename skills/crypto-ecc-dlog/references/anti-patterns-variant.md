# Anti-patterns variant — the loops to avoid

## The bound-fishing loop

`--nonce-bits` swept 64→256 hoping a `d` verifies — the bound comes from
the challenge statement or the observed `k` range, not brute force. Each
run is a probe against the budget.

## The sig-hoarding

Collecting hundreds of sigs for `hnp-ecdsa` — `m+1` lattice dims slow
pure-python LLL; the count formula gives the minimum, stay near it.

## The generic-dlog trap

`bsgs` on a huge `ord`, `pohlig-hellman` on `p-1 = 2q` — the gates exist to
stop exactly this. If the order resists, the bug is elsewhere (defect or
protocol).

## The single-sig stall

Rotating attacks on one signature — the math gives nothing with `m=1`.
Gather sigs or use the oracle.

## The wrong-family blind spot

`dlog.bsgs` on `Q = x·P` — `dlog` is multiplicative-group only; curve dlog
needs `ec.py` point ops with the same order logic.

## The verify-skip

Claiming the flag from a plausible `d` — the verify decides. A `d` that
doesn't reproduce `Q` isn't a key.

## The re-route blindness

A `p-1 = 2q` order where PH/BSGS both die → the intended bug is not dlog —
it's a defect curve, a nonce leak, or a protocol flaw. `decide.py` escalates.
