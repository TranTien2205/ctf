# Common mistakes deep — the operator errors that waste budget

## The count mistakes — the cheapest to make

- **`mt19937-clone` on 623 outputs** — the count IS the gate; nothing
  recovers. Collect one more.
- **`lcg-unknown-modulus` on 5 outputs** — one `u`, no gcd, `m` unpinned.
  Collect a 6th.
- **`berlekamp-massey` on `2w-1` bits** — underdetermined; the returned
  taps fit the prefix but aren't the generator. Collect one more bit.
- **running any attack before the count check** — the whole budget spent
  on a shape that cannot work.

## The rawness mistakes — the most damaging

- **feeding `x mod n` outputs to `lcg-recover`** — the states are reduced;
  the affine solve returns wrong `a`,`c`.
- **feeding floats to `mt19937-clone`** — `random()` isn't a 32-bit word;
  the clone is garbage.
- **feeding hex/base64 strings** — `--outputs` wants comma ints; decode.
- **a `randint`/`choice`/`shuffle` output treated as raw** — the word is
  post-processed.

## The convention mistakes — the subtle ones

- **`--low-bits` = the KEPT bits** — it's the DROPPED bits `b` in `x>>b`.
  Passing `32` for a `x>>32` leak on a 64-bit state is right; passing the
  kept `32` when only `16` are dropped is wrong. Re-read which is which.
- **`--taps` in the wrong convention** — 1-indexed-LSB vs 0-indexed vs
  MSB-indexed. `lfsr-predict` diverges → re-index.
- **`--outputs` order shuffled** — sort/dedup/reverse breaks "consecutive".

## The variant mistakes — the platform traps

- **`xorshift128.py` on `Math.random`** — V8 is `xorshift128+`, not
  `xorshift128` — wrong variant → wrong state.
- **Python `random` MT on PHP `mt_rand`** — different seeding/word handling
  — the clone fails.
- **treating `java.util.Random` as a generic LCG with unknown `a,c,m`** —
  it's a KNOWN `m=2^48, a, c` with `nextInt` leaking `x>>16` →
  `lcg-truncated`, not `lcg-unknown-modulus`.
- **`glibc rand()` as a plain LCG** — it's an additive feedback generator —
  a different recurrence.

## The param mistakes

- **`--modulus` guessed** — for `lcg-unknown-modulus` there IS no
  `--modulus` flag; feeding `m` skips the gcd step but only if `m` is
  right.
- **`--a`/`--c`/`--m` wrong for `lcg-truncated`** — all required; a wrong
  one poisons the lattice.
- **assuming `m=2^32`** — glibc `rand()` is `2^31`; `java.util.Random` is
  `2^48` — check the platform.

## The verification mistakes — the dishonest ones

- **recording `a`,`c`,`m` from a return without a held-back check** — a
  candidate, not a recovery.
- **matching `predict` to a training output** — verifies nothing (a wrong
  `a,c` can interpolate).
- **calling one lucky match a recovery** — reproduce a sequence.
- **recording a flag from a `flag{`-shaped string in the description** —
  not the recovered object.

## The class mistakes

- **running LCG recovery on a CSPRNG/`urandom`** — `gcd` won't fit; the
  stream isn't affine.
- **running BM on a combiner output** — `L ≈ n/2` → not a plain LFSR.
- **running `mt19937-clone` on a reseeding oracle** — the window is off.
- **assuming "looks random" means unattackable** — the whole class is
  "looks random but isn't".
