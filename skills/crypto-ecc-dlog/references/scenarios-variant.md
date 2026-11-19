# Scenarios variant — the handout shapes restated

## "The pair" — two signatures

`sigs.json` with two entries, `r` identical → `ecdsa-nonce-reuse`. The
one-command solve.

## "The service" — `sign(m)`

Deterministic `k` (same `m` → same `(r,s)`) → reuse impossible on same `m`;
collect sigs across `m`s, look for `r` repeat or bounded `k` → `hnp-ecdsa`.

## "The curve params" — `p a b G Q`

`Δ`/`#E`/`smoothness`/`bsgs` ladder — `singular_ec`/`smart_attack`/
`pohlig-hellman`/`bsgs`.

## "The statement" — `h = g^x mod p`

`smoothness` → `pohlig-hellman`; bounded `x` → `bsgs`.

## "The oracle" — point-multiply service

Unvalidated `P'` → invalid curve → `ec.py` fake curves → `bsgs`/`pohlig`
per response → CRT.

## "The JWT" — two ES256 tokens

`r||s` per token; same `r` → `ecdsa-nonce-reuse` → `d` → forge admin.

## "The leak" — `k` partial bits

`(t,u)` per sig → `hnp --t --u --modulus --bound`.

## "The secret-share" — `x` bounded

`bsgs --order <bound>` directly.
