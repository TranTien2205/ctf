# Real-world cases variant — the shipped attacks, compact

## Debian OpenSSL (2008)

`pid` seed — ~32k keys — enumerate `pid` → match. The bounded-seed case.

## PHP `mt_rand`

`mt_srand(small/leaked)` → `mt_rand` predictable — the PHP MT variant.

## `java.util.Random`

`m=2^48, a=0x5DEECE66D, c=0xB`, `nextInt`=`x>>16` → `lcg-truncated
--low-bits 16`.

## `drand48`/`lrand48`

Same `a`,`m` — `lrand48`=`x>>17` → `lcg-truncated --low-bits 17`.

## `Math.random` (V8)

`xorshift128+` + double — NOT `xorshift128` — the `+` variant.

## glibc `rand()`

Additive `x_i=x_{i-31}+x_{i-3}` — not a plain LCG.

## `srand(time(0))`

The classic bounded-seed — the window is the epoch.

## The pattern

Same families (LCG/LFSR/MT/xorshift/seed), platform-specific constants +
shapes — fingerprint the variant, meet its count + normalization.
