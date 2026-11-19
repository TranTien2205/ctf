# Scenarios — the challenge shapes

## The token/nonce oracle

- `GET /token`/`/nonce`/`/ticket` returns a "random" value.
- Collect consecutive → fingerprint → attack → predict the next → use it.

## The session-id stream

- `session_id`/`uid`/`api_key` minted by `random`/`rand()`.
- The full 624 → `mt19937-clone`; a shorter window → seed-search.

## The stream-ciphered flag

- `flag_ct = flag ⊕ lfsr_keystream`/`mt_keystream`/`lcg_keystream`.
- Recover the generator → the keystream → `ct ⊕ ks` → flag.

## The keygen

- A key is `next(prng)` — recover the state → derive the key → decrypt.

## The lottery/game

- "predict the next roll" — recover the generator → call it → flag.

## The signed/seeded artifact

- A `seed` field in the artifact → bound it → enumerate → match.

## The truncated leak

- A keygen/token leaks `x >> b` — `lcg-truncated --low-bits b`.

## The JS/browser generator

- `Math.random`/`java.util.Random`/`mt_rand` — the algorithm differs by
  platform but the family is the same; fingerprint the variant.
