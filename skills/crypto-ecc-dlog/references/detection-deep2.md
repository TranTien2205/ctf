# Detection deep 2 — the subtle signals

## The `r`-vs-`k` confusion

`r` is `x(k·G) mod n` — the *visible* part of `k`. Two signatures can have
the same `k` only if `r` matches (same `k·G` → same `x`). Checking `s` or
`z` for repeats is meaningless.

## The `z` reconstruction

`z` never arrives raw in a real sig — you compute it from the message:
`z = int(H(m))` truncated to `order_bits`. A `{"r","s","z"}` file entry
already has `z` computed; a `{"r","s","message"}` file needs hashing.

## The deterministic-nonce tell

`sign(m)` returns identical `(r,s)` on identical `m` → `k` is deterministic.
That's not a bug unless `k` is also predictable *across* messages — the
RFC 6979 path is hardened; the bug shapes are `k = f(timestamp)` or a
reset PRNG.

## The curve-order ambiguity

`#E` can be prime (secure), `p` (anomalous → broken), `p-1`/`p+1` (near —
check smoothness), or smooth (PH-able). A challenge that hides `#E` either
wants you to count it or intends a protocol bug.

## The `G` that isn't `G`

A supplied `G` with small `ord(G)` inside a smooth-order group → the secret
is small without the whole group being weak — `bsgs`/`pohlig` on `ord(G)`.

## The multi-sig-with-mixed-`k`

Some sigs have biased `k`, others fine — filter the biased subset for
`hnp-ecdsa`; the fine ones don't help.
