# Scenarios variant — the challenge shapes, compact

## The token oracle

`GET /token`/`/nonce`/`/ticket`/`/roll` → ints → LCG/MT/xorshift →
fingerprint → attack → predict → forge → flag.

## The session-id stream

`session_id=random`/`rand()`/`mt_rand` → 624 → `mt19937-clone`; `seed=
time()` → seed-search.

## The stream-ciphered flag

`flag_ct=flag⊕ks` → `flag{` prefix → BM → `lfsr-predict` → `ct⊕ks` →
flag.

## The keygen

`key=next(prng)` → recover state → derive key → decrypt → flag.

## The lottery/game

"predict the next" → recover → predict → win → flag.

## The seeded artifact

`seed`/`iat`/`created` field → bound → enumerate → match → flag.

## The truncated leak

`x>>b`/`x mod n` → `lcg-truncated --low-bits` / different model.

## The JS/browser

`Math.random`/`java.util.Random`/`mt_rand` → the platform variant → the
variant's attack.
