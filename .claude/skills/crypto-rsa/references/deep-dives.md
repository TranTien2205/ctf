# Deep dives — the long-form modules

## The construction

`n=p·q`, `φ=(p-1)(q-1)`, `ed≡1 mod φ`. `c=m^e mod n`. Every attack is a
violation of one of six factoring preconditions — a wrap, a gap, a shared
divisor, a smooth predecessor, an exponent relation, or a leak.

## The detection pipeline

```
handout → parameter-sheet → discriminator → bound-check → attack → pow-verify
```

The sheet names the shape (`n`,`e`,`c` counts, the leak, the keygen); the
discriminator picks the id; the bound is the falsifier.

## The six primitives and the attacks

| Primitive | The tell | The attacks |
|---|---|---|
| wrap | `e` small, `m` short | `small-e-root`,`nth-root`,`hastad` |
| gap | `next_prime`,`p+k` | `fermat` |
| divisor | ≥2 `n` / `p-1` smooth | `batch-gcd`,`pollard-pm1` |
| exponent | `e`~`n`,2 `e`,a `d`/`phi` leak | `wiener`,`boneh-durfee`,`common-modulus`,`factor-from-d` |
| partial | redacted `p`,`m` partial | `coppersmith-*` |
| relation | `m2=a·m1+b`,a fault,`dp` | `franklin-reiter`,`crt` |

## The bounds (the falsifiers)

- `d < n^0.25` wiener · `d < n^0.292` boneh-durfee
- window `≥ n^0.25` coppersmith-`β=½` · `|x| < n^(1/e)` partial-message
- `m^e < n` small-e · `≥e` coprime `n` hastad
- `gcd(e1,e2)=1` common-modulus · `|p-q|` small fermat · `B`≥`p-1` factor pollard
- `∏pi>m` / a fault / `dp` crt · linear relation franklin-reiter · `gcd(e,phi)>1` eth-root

## The recoveries

- factor → `rsa-decrypt` → `m`
- `d` → `rsa-decrypt` → `m`
- `m` direct → `pow` verify

## The toolchain

`tools/crypto_attack.py list` — every id + its bound; `<id> --help` the flags;
stdlib-only, pure-python LLL (`fpylll` absent → slower, same reach).

## The honest status

**Catalogue** — no local solve. Published-standard; `../field-notes.md` grows with
real solves.
