# Platform PRNGs — detection and recovery per runtime

Deep module: the generator is usually the platform's own `rand()`/`random()`/`Random`,
not a cipher. This module names the identifiable, recoverable members of the platform
PRNG family and the recovery each accepts. A generic algorithm attack only applies
when source shows the generator is custom — see `detection-matrix.md` first.

## Detection table — which platform RNG this is

| Surface signal | Generator | Attack |
|---|---|---|
| C/C++ `rand()` with `srand(seed)`, glibc | additive feedback `random()` — r=31/34 | recoverable: 32 outputs identify state |
| C `rand()` = MSVC/ANSI LCG (`x = x*214013+2531011`) | 15-bit LCG | `lcg-recover` m=2^32, take bits 16..30 |
| Java `java.util.Random` | 48-bit LCG, `next()` returns high bits | clone from 2 outputs (48-bit brute, or one `nextLong`/`nextInt` pair) |
| Java `Math.random()` / `SecureRandom` | secure — not attackable | reclassify: needs a different bug |
| PHP `mt_rand()` / `mt_srand()` | MT19937 | `mt19937-clone` needs 624; PHP-specific seed-recovery tools for fewer |
| PHP `rand()` / `srand()` | glibc `random()` on Linux | additive-feedback recovery |
| Go `math/rand` (pre-1.20 default) | lagged Fibonacci, 607-word state | recover from ~607 outputs; or seed-search `rand.Seed` |
| Go 1.20+ `math/rand` global | ChaCha8-seeded, auto-seeded | not state-recoverable from outputs alone — check Go version |
| Go `rand.New(rand.NewSource(seed))` | deterministic, seeded | seed-search if seed is time/weak |
| Python `random` | MT19937 | `mt19937-clone` — 624 outputs untemper |
| Python `random.SystemRandom` / `secrets` | os.urandom | not attackable — reclassify |
| .NET `System.Random` | Knuth subtractive, 55-word state | recover from ~55 outputs; `Next()` is seeded by Environment.TickCount |
| Node `Math.random()` | xorshift128+ (V8) | `xorshift128.py` — clone from a handful of outputs |
| Rust `rand::SmallRng`/`StdRng` | xoshiro/ChaCha | not naively invertible from output — check the RNG named |

## The recovery rule

Match the attack to the platform's generator, not to the word "random". If source
names `random.seed(t)` / `srand(time)` / `rand.Seed(now)` with a small seed space,
seed-search beats state recovery — the seed is the flag's entropy, not the state.
If the platform RNG is ChaCha-based or `SecureRandom`/`secrets`/`SystemRandom`, no
output-only attack applies: reclassify — the challenge must want a different bug.

## Per-platform notes

- **glibc `rand()` == `random()`** on Linux — NOT the naive 31/34-tap LFSR. It is a
  non-linear additive feedback generator; ~32 consecutive outputs recover state.
  Do not feed it to `lcg-*` — it is not an LCG.
- **Java `Random`** — 48-bit state; `nextInt()` leaks the high 32 bits, `nextLong()`
  leaks the full state across two calls. Two outputs narrow state to a brute-able
  window; `nextLong()` clones outright. `SecureRandom` is a different beast — skip.
- **PHP `mt_rand`** — same MT19937 core as Python, but PHP re-seeds from a tiny
  space; with <624 outputs, seed-recovery (brute `mt_srand` candidates) is the path.
- **Go** — version matters: pre-1.20 default `math/rand` is deterministic and seeded
  by `rand.Seed`; 1.20+ auto-seeds with runtime entropy (unrecoverable). Read `go.mod`
  or the binary's Go build version before choosing.
- **V8 `Math.random()`** — xorshift128+, state is 2 doubles; `xorshift128.py --outs`
  recovers and `--predict` extends. MurmurHash seeding is not relevant here.
- **.NET `System.Random`** — Knuth's subtractive generator; `Next()` seeded by
  `Environment.TickCount` (~600ms window) → small seed search is usually enough.

## Boundary

A platform RNG backed by OS entropy (`secrets`, `SystemRandom`, `SecureRandom`,
`crypto/rand`, `getrandom`) is not a PRNG attack surface. If the only RNG the
challenge exposes is one of those, the intended bug is elsewhere — do not burn the
budget forcing `lcg-*`/`mt19937-clone` onto a secure source.

## First confirming probe per platform

Identify the runtime, then run the one probe that names the generator. These are
detection probes — each produces a signal, not yet a recovery.

| Runtime | Cheapest identifying probe | What confirms it |
|---|---|---|
| C/C++ on Linux | `strings`/`nm` for `srand`/`rand`/`random` | a `rand()`/`random()` call, no custom LCG |
| Java | `javap -c` / source for `new Random` / `Math.random` | `java.util.Random` vs `SecureRandom` named |
| PHP | source for `mt_rand`/`rand`/`mt_srand`/`srand` | which of mt/glibc the calls hit |
| Python | source for `random.`/`secrets`/`os.urandom` | `random` (MT) vs `secrets`/`SystemRandom` |
| Go | `go.mod` version + `math/rand` vs `crypto/rand` | `rand.Seed` present ⇒ seeded, searchable |
| Node/V8 | `Math.random` in source, V8 engine | `xorshift128.py` applies |
| .NET | `new Random(` / `Random.Shared` | `System.Random` subtractive generator |

The probe answers "which generator" before any recovery command runs. Only after
the table names a recoverable generator do the `crypto_attack.py` ids or the
seed-search path apply. A generator the table marks not-attackable is a
reclassification signal, not a reason to keep pushing outputs at `lcg-*`: stop,
name the actual bug class, and let `tools/decide.py` pick the next layer rather
than spend the budget proving a negative the table already predicts.

The falsifier for every platform row is identical and is the class falsifier:
recover the state or seed, predict the next output, and require the prediction
to equal a held-back output exactly. A statistical resemblance — same range,
similar distribution, plausible values — is not recovery.

## Cross-references

`detection-matrix.md` · `mechanism.md` · `attack-catalogue.md` ·
`seed-search-deep.md` (time/weak seed search) · `../field-notes.md`.
