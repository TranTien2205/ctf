# Edge cases deep — the shapes that aren't the textbook

## The non-consecutive stream

- **Other callers consume the generator** — a shared `random` module where
  the app also calls `random` between your observations. Your outputs have
  gaps. Fix: find a call path where the generator is private, or collect
  every call.
- **A `seed()` inside the window** — the index resets; the collected
  outputs span two streams. Fix: bound to one contiguous window.
- **A reseeding oracle** — `srand(time())` per request → each output a
  fresh seed → seed-search, not a stream recovery.

## The post-processed stream

- **`randint(a,b)`/`choice`/`shuffle`** — `G` post-processed. `randint`'s
  mapping isn't a raw word; reconstruct or fingerprint the underlying
  calls.
- **`random()` floats** — `getrandbits(53)/2^53` — two words per float;
  convert the float pair or re-collect as `getrandbits`.
- **`hex`/`b64`/`str`** — decode to the int.
- **`x mod n`/`x & mask`** — reduced — the affine structure shifts per
  wrap; not the raw `x`.

## The truncated leak variants

- **`x >> b`** (high bits kept) → `lcg-truncated --low-bits b`.
- **`x & ((1<<k)-1)`** (low bits kept) → different mask — the HNP model
  changes.
- **`x mod n`** → the reduced state — each wrap subtracts `n` — a
  different model.
- **`getrandbits(k<32)`** → the low bits of a word dropped — a truncated
  word.

## The keyed/seeded variants

- **`random.seed(secret)`** — the seed isn't enumerable; the output is a
  keyed stream → not this class unless the seed is leaked.
- **`secrets.token_*`/`os.urandom`** — CSPRNG → out of class.
- **`srand(user_input)`** — attacker-controlled seed → a different attack
  (fix the seed, the stream is yours).

## The platform-variant generators

- **`mt_rand`/`mt_srand`** (PHP) — MT19937 with PHP's own seeding and a
  `MT_RAND_PHP` broken mode — the variant differs from Python's `random`.
- **`java.util.Random`** — a 48-bit LCG — `lcg-truncated` with
  `low-bits=16` on `nextInt`.
- **`Math.random`** (V8) — `xorshift128+` + a double — not `xorshift128`.
- **`glibc rand()`** — an additive feedback generator, not a plain LCG.
- **`arc4random`/`SecureRandom`** — CSPRNG → out of class.

## The combined/nonlinear generators

- **LFSR + nonlinear filter** — `f(x_t)` over the register — BM gives high
  complexity → correlation/filter attack, not plain LFSR.
- **multiple LFSRs combined** — `x^y^z` or a majority — complexity ≈
  product → correlation attack per-LFSR.
- **`rand() ^ rand()`** — a combined LCG — the structure is masked.

## The small-leak generators

- **only 3 outputs** — `lcg-recover` works (m known) but `lcg-unknown-modulus`
  can't.
- **only a hash of the output** — the state isn't observable — different
  class (preimage/brute-force).

## The verification edge

- **a single coincidence** — `predict` matching once by luck is not a
  recovery — reproduce a sequence.
- **`predict` "close"** — bit-for-bit only; off-by-one is a fail.
