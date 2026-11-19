# Recon order — the oracle's first probes

## The oracle probes in order

1. **`/token`/`/nonce`/`/rand` baseline** — what does one call return?
   Int/float/hex/bits? The shape names the family.
2. **Repeat calls** — deterministic (same output per call → not a stream)
   or a stream (each call advances)?
3. **Collect consecutive** — how many can you hold? The count gates the
   attack.
4. **Error/edge probing** — does a bad request leak `m`, the seed, or the
   generator name?

## The reads each probe buys

| Probe | Reads |
|---|---|
| baseline | output shape → family hint |
| repeat | stream vs fixed |
| collect | the count → which attack |
| error | `m`/seed/gen-name leaks |

## The order rationale

- shape first — hex/float/bits name the family.
- consecutive second — the whole premise.
- count third — the attack floor.

## The boundary

- A `sign`-like oracle → the output may be post-processed → normalize.
- A reseeding oracle (`srand` per call) → not a stream → seed-search.
