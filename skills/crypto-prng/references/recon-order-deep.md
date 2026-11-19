# Recon order deep — the oracle's probes, with the why

## Probe 1 — the baseline call

`GET /token`/`/nonce`/`/rand`/`/roll` once.

**Buys**: the output SHAPE — int/float/hex/bits — which names the family
before any statistics. A `0.47...` float is a `random()`/`Math.random`
variant; a raw int is LCG/MT/xorshift; a `0/1` bit is LFSR.

## Probe 2 — the repeat call

Call it twice, same params.

**Buys**: stream vs fixed. Same output → the generator reseeds per call
or the endpoint is fixed — different problem. Different output → a stream.

## Probe 3 — the collection

Call it `k+1` times, no other calls interleaved.

**Buys**: the consecutive stream. `k` meets the attack's floor; `+1` held
back for verify. A GAP (another caller consumed the generator) shows as a
non-affine difference — collect every call or find a private oracle.

## Probe 4 — the error probe

`?n=abc`, `?count=-1`, a bad request.

**Buys**: leaks — `m`, the seed, the generator name, a stack trace
naming `random`/`mt_rand`/`java.util.Random`. A verbose error is the
cheapest fingerprint.

## Probe 5 — the count measure

How many outputs can you hold before the oracle stops?

**Buys**: the count ceiling — decides `mt19937-clone` (needs 624) vs
seed-search (needs a bounded window) vs a smaller-count attack.

## Probe 6 — the parameter read

Read source for `MOD`/`a`/`c`/taps/`seed=`/`srand`.

**Buys**: the params that route LCG (`m`? → recover vs unknown-modulus;
`a,c,m`+`x>>b` → truncated) and LFSR (taps? → predict vs BM).

## The order rationale

shape → stream-vs-fixed → count → params → attack. Each probe buys the
gate for the next: the shape names the family, the count gates the
attack, the params pick the specific attack within the family.

## The boundary reads

- A `seed()`/`srand()` in the handler → the stream is reseeding →
  seed-search, not a state recovery.
- A `mod n`/`>>b`/`&mask` in the output → not raw → normalize/truncated.
- A `urandom`/`secrets` → out of class.
