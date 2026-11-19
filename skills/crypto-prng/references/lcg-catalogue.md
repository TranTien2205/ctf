# LCG catalogue — every LCG attack and platform, indexed

## The attack ids

| Id | Known | Leak | Count | Tool |
|---|---|---|---|---|
| `lcg-recover` | `m` | raw `x` | 3 | `crypto_attack.py lcg-recover` |
| `lcg-unknown-modulus` | none | raw `x` | 6 | `crypto_attack.py lcg-unknown-modulus` |
| `lcg-truncated` | `a`,`c`,`m` | `x>>b` | required | `crypto_attack.py lcg-truncated` |

## The platform LCGs

| Generator | `m` | `a` | `c` | Leak | Attack |
|---|---|---|---|---|---|
| `java.util.Random` | `2^48` | `0x5DEECE66D` | `0xB` | `nextInt`=`x>>16` | `lcg-truncated --low-bits 16` |
| `drand48`/`lrand48` | `2^48` | `0x5DEECE66D` | `0xB` | `>>16`/`>>17` | `lcg-truncated` |
| glibc `rand()` old | `2^31` | `1103515245` | `12345` | `x>>16&0x7fff` | `lcg-truncated` |
| `minstd`/`park-miller` | `2^31-1` | `16807` | `0` | `x` | `lcg-recover` |
| MSVC `rand()` | `2^32` | `214013` | `2531011` | `x>>16&0x7fff` | `lcg-truncated` |
| Numerical Recipes | `2^32` | `1664525` | `1013904223` | `x` | `lcg-recover` |

## The output-shape → attack

| Leak | Attack |
|---|---|
| raw `x`, `m` known | `lcg-recover` |
| raw `x`, `m`? | `lcg-unknown-modulus` |
| `x>>b`, `a`,`c`,`m` | `lcg-truncated` |
| `x mod n` | DIFFERENT — not these |
| float/`randint` | normalize / variant |

## The falsifier → kill

| Falsifier | Kill |
|---|---|
| `gcd→0/1` | not affine |
| `predict!=held` | wrong params/shape/variant |
| `gcd(x1-x0,m)!=1` all | `a` non-invertible |

## The files

`per-attack-lcg-*` the attacks · `lcg-deep`/`lcg-catalogue` the family ·
`per-family-lcg*` the internals · `real-world-cases*` the platforms.
