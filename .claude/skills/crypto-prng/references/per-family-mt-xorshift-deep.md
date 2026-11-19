# Per-family MT/xorshift deep — the word-stream generators

## Two families, one discipline

MT19937 and xorshift128 both emit raw 32-bit words — the difference is
the count floor (624 vs 4) and the recovery mechanism (untemper vs
linear solve). Both are linear-state generators — their output is an
invertible function of the state.

## MT19937 — the state monster

- **state**: 19968 bits = 624×32 words.
- **`G`**: `temper` — a 4-step invertible shift/XOR mask — `untemper`
  undoes it.
- **count**: exactly 624 consecutive raw `getrandbits(32)` words.
- **the attack**: `mt19937-clone` — untemper each of the 624 words → the
  state → `predict_next`.

### The MT traps — all four kill the clone

- `<624` — the gate; collect more or seed-search.
- **non-consecutive** — a shared `random` module injects gaps.
- **non-raw** — `random()`/`randint`/`choice`/`getrandbits(k<32)` are
  post-processed.
- **reseed** — `seed()` in the window resets the index.

### The MT variants

- **`random` (Python)** — standard MT19937 → `mt19937-clone`.
- **`mt_rand` (PHP)** — MT19937 with PHP seeding + a broken `MT_RAND_PHP`
  mode — the variant differs; a Python `random` clone on `mt_rand` fails.
- **`std::mt19937` (C++)** — same core, different seeding.
- **`numpy.random`** — MT19937 or PCG64 — fingerprint which.

## xorshift128 — the 4-word clone

- **state**: 128 bits = 4×32 words.
- **`G`**: the whole word `w` — no scrambling.
- **count**: exactly 4 consecutive words.
- **the attack**: `xorshift128.py` — 4 outputs pin the 128-bit state.

### The xorshift variants — the #1 trap

- **`xorshift128`** — the plain one → `xorshift128.py`.
- **`xorshift128+`** — V8 `Math.random` — `s0+s1` output — NOT covered.
- **`xorshift64*`** — one word, multiply — NOT covered.
- **`xoroshiro`/`xoshiro`** — rotations — NOT covered.

## The shared verification

`predict == held-back` — for both. `mt19937-clone --count 1` vs word 625;
`xorshift128 --predict 1` vs the 5th word.

## The shared boundary

- **`Math.random`** is `xorshift128+` + a double — neither MT nor
  `xorshift128` — a different variant.
- **a keyed `random.seed(secret)`** — not enumerable → different class.
- **`numpy`/`torch`/`SecureRandom`** — a different generator or a CSPRNG.

## The discriminator

| Count available | Generator | Attack |
|---|---|---|
| 624+ raw words | MT19937 | `mt19937-clone` |
| 4 raw words | xorshift128 | `xorshift128` |
| <624 raw words + small seed | either | seed-search |
| floats/doubles | `random()`/`Math.random` | normalize / variant |
