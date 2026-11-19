# Theory boundary — where the recoveries stop working

## The linearity boundary

The attacks work because `F`/`G` are linear/invertible. The boundary is
where linearity ends:

- **combiner LFSR** — `f(x_1,...,x_k)` nonlinear → `L≈n/2` → BM fails →
  correlation attack.
- **filtered LFSR** — a nonlinear `f` over one register → high
  complexity → the falsifier.
- **CSPRNG** — `G` one-way (AES/hash) → no state leak → out.
- **keyed cipher** — `G(state, key)`, `key` unknown → the key is the
  secret, not the state → `crypto-symmetric-oracle`.

## The count boundary

The `S/O` floor is hard — fewer than `S` output bits can't pin `S` state
bits. `<624` MT, `<4` xorshift, `<2w` LFSR, `<6`/`3` LCG — the floor is
information-theoretic, not a tool limitation.

## The seed boundary

`seed` enumerable only if `|seed|` is bounded — `time()`/`pid`/`id` are
small; `os.urandom`/`secrets`/`crypto.getRandomValues` are not. The
boundary is the seed's entropy, not the generator.

## The rawness boundary

`G` = `x>>b`/`x mod n`/float/`randint` — the output is a transform of
`x`. `>>b` → truncated (HNP); `mod n` → reduced (a different model);
float/`randint` → post-processed (normalize or the word). The boundary is
whether the transform preserves enough of `x` to recover.

## The variant boundary

`mt_rand`/`java.util.Random`/`Math.random`/`glibc rand`/`drand48` —
the FAMILY is right but the constants/seeding/variant differ — the same
attack shape, different `a`,`c`,`m`/variant. The boundary is the exact
algorithm, not the family.

## The falsifier is the boundary

`predict != held` / `gcd→0` / `L≈n/2` — the theory running in reverse:
the structure isn't there → reclassify.
