# Mechanism catalogue — every attack, its primitive, its bound

## The primitives and their attacks

| Primitive | Attacks | Bound | Verify |
|---|---|---|---|
| wrap | `small-e-root`,`nth-root`,`hastad` | `m^e<n` / `∏n>m^e` | `pow(m,e)==c/x` |
| gap | `fermat` | `\|p-q\|` small | `p*q==n` |
| divisor | `batch-gcd` | a collision | `p*q==n` |
| divisor | `pollard-pm1` | `B`≥`p-1` factor | `gcd=p` |
| exponent | `common-modulus` | `gcd(e1,e2)=1` | `pow==c` |
| exponent | `wiener` | `d<n^0.25` | `pow(c,d,n)==m` |
| exponent | `boneh-durfee` | `d<n^0.292` | `pow(c,d,n)==m` |
| exponent | `factor-from-d` | `d`/`phi` held | `p*q==n` |
| partial | `coppersmith-high-bits`,`-core` | window≥`n^0.25` | `p\|n` |
| relation | `franklin_reiter` | `m2=a·m1+b` | `pow==c` |
| relation | `crt` | `∏pi>m`/fault/`dp` | `pow==c`/`gcd=q` |
| leak | `rsa-decrypt`,`eth-root` | factors held | `pow==c` |

## The primitive → the signal

- **wrap** — `e` small, `m` short, or same `m` to `e` n's.
- **gap** — `next_prime`,`p+k`,shared seed in keygen.
- **divisor** — ≥2 moduli, or a "weak prime" hint.
- **exponent** — `e` ~`n`, two `e` on one `n`, a `d`/`phi` leak.
- **partial** — a redacted key, a partial `m`, a centred guess.
- **relation** — related `m`'s, residues, a faulty sig.
- **leak** — the private value itself.
