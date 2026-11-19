# Edge cases — the disguised limits

## The format edge cases

- **hex/base64 outputs** → decode to ints first.
- **floats [0,1)** → `int(v*2**53)` for `random.random` — or accept it's not
  a raw-word clone.
- **`mod n` applied** → the observation isn't the state — a reduced
  problem.
- **`randint`/`choice`/`shuffle`** → the generator output is post-processed
  — the word isn't what you see.

## The math edge cases

- **`m` shares a factor with `x1-x0`** → `a`'s inverse missing → gather
  outputs or factor `m`.
- **`m` composite** → the gcd trick may return a multiple — factor it.
- **LFSR + nonlinear combiner** → BM complexity huge → not a plain LFSR.
- **MT reseed mid-stream** → alignment breaks — split the windows.

## The oracle edge cases

- **rate-limited oracle** → can't reach 624 — the challenge is seed-search
  or a different bug.
- **error oracle** → does an error leak state bits?
- **gap in outputs** → "consecutive" broken — the clone alignment fails.

## The seed edge cases

- **`time()` vs `int(time())`** → the seed is the int, not the float.
- **pid+time mixed** → two-factor seed — bound both.
- **`mt_rand` (PHP)** → different MT seeding/word count — variant.

## The class edge cases

- **CSPRNG source** → `os.urandom`/`secrets` → wrong class entirely.
- **keyed hash/HMAC token** → not a PRNG recovery — a different class.
