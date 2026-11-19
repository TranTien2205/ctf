# Evasion variant — the disguises catalogued by what they hide

## Disguises that hide the generator

- **`next()`/`rand()`/`secure_random()`/`get_random()`** — a wrapper name;
  usually LCG/LFSR/MT inside. Read the implementation, don't trust the
  name.
- **a `Random`/`PRNG`/`RNG` class** — same; the class name hides the
  algorithm.
- **`os.urandom` used NON-entropy-wise** — `urandom` seeded by `time()` in
  a challenge is still `time()` — read the actual seed source.

## Disguises that hide the state

- **hex/base64/`str`** — a format, not a transform — decode.
- **`x mod n`/`x & mask`** — a reduced state — the affine structure shifts.
- **`x >> b`** — truncated — `lcg-truncated`.
- **`randint`/`choice`/`shuffle`** — post-processed — the word is mapped.
- **`random()`/`uniform`** — a `2^53` float pair — not a raw word.

## Disguises that hide the seed

- **`seed(time())` vs `seed(int(time()))`** — same window.
- **`seed(time()*1000)`** — ms — 1000× the window.
- **`seed(pid)`/`seed(pid^time)`/`seed(pid+time)`** — pid range `0..32k`,
  or two-factor.
- **`seed(user_id)`/`seed(counter)`** — enumerable if the id is small.
- **`seed(os.urandom)`/`seed(secrets)`** — NOT enumerable → out of class.

## Disguises that hide the stream's consecutiveness

- **a shared `random` module** — the app calls `random` too — your outputs
  have gaps.
- **a reseeding handler** — `seed()` per request — each output a fresh
  seed.
- **interleaved calls** — `/token` and `/roll` share one generator — the
  streams interleave.

## Disguises that hide the platform variant

- **`mt_rand`/`mt_srand`** labeled "random" — PHP MT.
- **`java.util.Random`** — the 48-bit LCG.
- **`Math.random`** — V8 `xorshift128+`.
- **`numpy.random`/`torch.rand`** — MT19937 or PCG64 — fingerprint.
- **a custom `next()`** that's an LCG/LFSR in disguise — fingerprint the
  structure, not the name.

## Disguises that hide the verification

- **a `flag{`-shaped string in the description** — not the recovered
  object.
- **one lucky `predict` match** — reproduce a sequence.
- **"the state looks plausible"** — bit-for-bit `predict==held` only.
- **statistical uniformity** — not predictability.

## The unifying disguise

The hardest disguise is a generator that's exactly what it claims but fed
a bounded seed — `random.seed(int(time()))` "looks" like a CSPRNG but is
a seed-search. Read the seed, not the generator's reputation.
