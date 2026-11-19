# Real-world cases — the attacks that left the lab

## Debian OpenSSL weak keys (2008)

A line removed from `md_rand` reduced the seed to the pid — ~32k keys.
The exact `pid`-seed-search shape; the whole attack is enumerating the
seed window.

## PHP `mt_rand` session/token attacks

`mt_rand`/`mt_srand` — the PHP MT. With a leaked seed or a seed shaped like
`time()`/`pid`, tokens become enumerable. The `mt_rand` variant differs
from `mt19937` in seeding and word handling — fingerprint the variant.

## `java.util.Random` — the LCG

`java.util.Random` is an LCG (`a=0x5DEECE66D`, `c=0xB`, `m=2^48`) — the
`lcg-*` family with known params; the truncated-`nextInt` leak maps to
`lcg-truncated`.

## glibc `rand()`/`random()`

`rand()` is an LCG/`TYPE_3` additive generator — recoverable from outputs;
the classic LCG-target.

## `Math.random` (xorshift128+)

V8's `Math.random` is `xorshift128+` — a variant of the xorshift family;
`xorshift128.py` covers the plain `xorshift128`, `128+` needs its own.

## Netscape/early TLS seeds

`time()+pid` seeds — the seed-search case.

## The pattern

Every real-world case is a fingerprint + a bounded seed or a
recoverable-from-outputs state — the exact families the corpus maps.
