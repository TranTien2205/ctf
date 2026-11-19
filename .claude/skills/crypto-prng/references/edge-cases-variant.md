# Edge cases variant — the non-textbook shapes, compact

## Output edges

- hex/`0x` → `int(x,16)`; base64 → decode; `str` → `int`.
- `x mod n`/`x&mask` → reduced — a different model from `x>>b`.
- `x>>b` → `lcg-truncated --low-bits b`.
- `randint`/`choice`/`shuffle` → post-processed — map to the word.
- `random()`/`uniform`/`Math.random` → float — `2^53` pair / `128+`.

## Stream edges

- gaps (shared `random`) → private oracle / collect every call.
- reseed in window → one contiguous window.
- reseed per request → seed-search.
- interleaved endpoints → separate streams.

## Variant edges

- `mt_rand`/`mt_srand` → PHP MT.
- `java.util.Random` → `lcg-truncated --low-bits 16`, `m=2^48`.
- `Math.random` → `xorshift128+`.
- `glibc rand()` → additive, not LCG.
- `drand48`/`lrand48` → `lcg-truncated --low-bits 16/17`.
- `numpy`/`torch` → MT or PCG64 — fingerprint.
- `arc4random`/`SecureRandom`/`urandom`/`secrets` → OUT.

## Combined edges

- LFSR + filter → correlation, not BM.
- `rand()^rand()` → masked.
- combiner-LFSR → `L≈n/2` → out of plain-LFSR.

## Verification edges

- one lucky match → reproduce a sequence.
- `predict` "close" → bit-for-bit only.
- `flag{` in description → not the object.
