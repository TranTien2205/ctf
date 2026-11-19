# Scenarios — the handout shape → the first command

## Two raw `(r, s)` values

→ scan `r`s → `crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n`.

## A `sign(m)` endpoint/binary

→ collect sigs (same `m` twice: same `(r,s)` = deterministic, different =
random). If deterministic and `r` differs across messages → gather for
`hnp-ecdsa` if nonce is bounded; if `r` repeats → `ecdsa-nonce-reuse`.

## `h = g^x mod p` with `p` small

→ `smoothness --n (p-1)` → `pohlig-hellman` or `bsgs`.

## Custom `p, a, b`

→ `#E` count → `smart_attack` if `#E == p`; `Δ` → `singular_ec` if `0`;
`smoothness --n #E` → `pohlig-hellman` if smooth.

## A "nonce" that looks like a timestamp

→ `hnp-ecdsa --sigs sigs.json --order n --nonce-bound <ts-range>`.

## A service multiplying your point

→ invalid-curve — `ec.py` for fake-curve construction, `bsgs`/`pohlig`
per response, CRT.

## A `jwt` with ES256 signature and a second one

→ the two `r`s — if equal → `ecdsa-nonce-reuse` → forge admin `jwt`.

## `x` stated bounded

→ `bsgs --order <bound>` directly.
