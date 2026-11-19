# Per-family LCG deep — the affine generator, every variant

## The family

`x_{i+1} = a·x_i + c mod m` — the oldest and most common PRNG. Every LCG
attack is a different slice of "what's known": `m` only → `lcg-recover`;
nothing → `lcg-unknown-modulus`; `a,c,m` + a high-bit leak →
`lcg-truncated`.

## The three attacks — the decision

| Known | Leak | Attack |
|---|---|---|
| `m` | raw `x` | `lcg-recover` |
| nothing | raw `x` | `lcg-unknown-modulus` |
| `a`,`c`,`m` | `x>>b` | `lcg-truncated` |

The "known" column IS the discriminator — check source for `m`,`a`,`c`
before picking.

## `lcg-recover` — m known

3 raw outputs + `m` → `a = (x2-x1)(x1-x0)^{-1}`, `c = x1-ax0`. The only
obstruction is a non-invertible difference on composite `m`.

## `lcg-unknown-modulus` — nothing known

6+ raw outputs → telescope `t_i` → `gcd(u_i)` → `m` → `lcg-recover`. The
gcd is the whole attack — a non-LCG collapses it to 0/1 (the falsifier).

## `lcg-truncated` — high bits only

`a`,`c`,`m` known + `h_i = x_i>>b` → a Hidden-Number lattice → the `l_i`.
The `--low-bits` is `b` (dropped), the most common operator error.

## The platform LCGs — the constants

| Generator | `m` | `a` | `c` | Leak |
|---|---|---|---|---|
| glibc `rand()` (old) | `2^31` | `1103515245` | `12345` | `x>>16 & 0x7fff` |
| `minstd`/`park-miller` | `2^31-1` | `16807` | `0` | `x` |
| `java.util.Random` | `2^48` | `0x5DEECE66D` | `0xB` | `nextInt`=`x>>16` |
| `drand48`/`lrand48` | `2^48` | `0x5DEECE66D` | `0xB` | `x>>16/17` |
| MSVC `rand()` | `2^32` | `214013` | `2531011` | `x>>16 & 0x7fff` |
| Numerical Recipes | `2^32` | `1664525` | `1013904223` | `x` |

`java.util.Random`/`drand48` share `a`,`m` — `nextInt`/`lrand48` leaking
high bits → `lcg-truncated --low-bits 16`.

## The shape question — the biggest trap

`x` raw? → the closed-form attacks. `x>>b`? → `lcg-truncated`. `x mod n`?
→ a DIFFERENT problem (reduced, not truncated). float? → normalize.

## The verification

`predict_next == held-back` — for every LCG attack.

## The boundary

- An additive-feedback `glibc rand()` (`x_i = x_{i-31}+x_{i-3}`) is NOT a
  plain LCG — a different recurrence.
- A combined LCG (`rand()^rand()`) — masked structure.
- A keyed/seeded `random.seed(secret)` — not enumerable → different class.
