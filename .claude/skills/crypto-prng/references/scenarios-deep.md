# Scenarios deep — the challenge shapes with the entry signals

## The token/nonce oracle — deep

**Shape**: `GET /token`/`/nonce`/`/ticket`/`/roll` returns a "random" value;
each call advances the generator.

**Entry signals**: a stream of ints → LCG/MT/xorshift; a bitstream →
LFSR; a time-coupled value → seed-search.

**The play**: collect consecutive → fingerprint → the matching attack →
predict the next → use it on the authenticated endpoint → flag.

**The gate**: `predict == held` before the forged call — a wrong predict
wastes the request.

## The session-id stream — deep

**Shape**: `session_id`/`uid`/`api_key` minted by `random`/`rand()`/
`mt_rand`.

**Entry signals**: `getrandbits(32)` in source → MT clone needs 624;
`random.seed(time())` → seed-search.

**The play**: 624 → `mt19937-clone`; a reseeding handler or `seed=time()`
→ seed-search.

**The gate**: count vs seed-bound — whichever is feasible is the route.

## The stream-ciphered flag — deep

**Shape**: `flag_ct = flag ⊕ keystream`, the keystream from an LFSR/LCG/MT.

**Entry signals**: a bitstream + a `flag{`/`CTF{` known prefix →
keystream → BM.

**The play**: `berlekamp-massey` → `lfsr-predict --count` → `ct ⊕ ks` →
flag. Or an LCG/MT keystream → the corresponding state recovery.

**The gate**: a known-plaintext prefix is required for the keystream — no
`pt` → no `ks` → a different entry (source-read the generator).

## The keygen — deep

**Shape**: a key is `next(prng)` or `prng-derived`.

**Entry signals**: the keygen source names the generator and the leak
shape (`x>>b`, `x mod n`, raw).

**The play**: recover the state → derive the key → decrypt → flag.

**The gate**: the leak shape names the attack — `x>>b` → `lcg-truncated`.

## The lottery/game — deep

**Shape**: "predict the next roll/draw/outcome" — a pure prediction game.

**Entry signals**: the roll source — `random`/`rand`/custom `next()`.

**The play**: recover → predict the next roll → win → flag.

**The gate**: `predict == held` before betting — a wrong call loses.

## The signed/seeded artifact — deep

**Shape**: a `seed`/`iat`/`created` field in the artifact bounds the
window.

**Entry signals**: a timestamp/pid field + a `random`-derived value.

**The play**: bound the window → `random.seed(ts)` → match → predict →
flag.

**The gate**: `iat`/`created` collapses `|seed|`; absent it, the window
may be unbounded → not seed-search.

## The truncated leak — deep

**Shape**: a keygen/token leaks `x >> b` or `x mod n`.

**Entry signals**: `>> b` → `lcg-truncated`; `mod n` → a different model.

**The gate**: `--low-bits` = `b` dropped.

## The JS/browser generator — deep

**Shape**: `Math.random`/`java.util.Random`/`mt_rand` — a platform variant.

**Entry signals**: the platform names the variant — `Math.random` =
`xorshift128+`; `java.util.Random` = a 48-bit LCG; `mt_rand` = PHP MT.

**The play**: the platform variant's attack — `xorshift128+` isn't
`xorshift128`; `java.util.Random.nextInt` → `lcg-truncated --low-bits 16`.

**The gate**: fingerprint the variant — the family is the same but the
constants/conversions differ.
