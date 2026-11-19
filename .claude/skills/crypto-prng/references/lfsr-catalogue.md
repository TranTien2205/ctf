# LFSR catalogue — every LFSR attack and variant, indexed

## The attack ids

| Id | Known | Leak | Count | Tool |
|---|---|---|---|---|
| `berlekamp-massey` | none | bits | 2w | `crypto_attack.py berlekamp-massey` |
| `lfsr-recover` | `w`[,taps] | bits | ≥2w | `crypto_attack.py lfsr-recover` |
| `lfsr-predict` | `taps`,`w` | bits | ≥w | `crypto_attack.py lfsr-predict` |

## The input forms

| Form | Flag |
|---|---|
| comma bits | `--bits 0,1,...` |
| hex | `--keystream-hex <hex>` |
| file | `--bits-file f` |

## The taps convention

`--taps` = 1-indexed-from-LSB. A degree-`d` polynomial tap maps to `w-d`.
Wrong convention → mirrored polynomial → `predict` diverges.

## The stream-cipher shape

`ct = pt ⊕ keystream` — a `flag{`/`CTF{` known prefix yields keystream
bits → BM → `lfsr-predict --count 8*len` → `ct ⊕ ks` → flag.

## The variants

- **Fibonacci** — the standard; what the tools model.
- **Galois** — XOR on the register — BM still works on the bits.
- **combiner/NLF** — nonlinear `f` over k LFSRs — `L≈n/2` → correlation.
- **shrinking/self-shrinking** — irregular clock → high complexity.

## The falsifier → kill

| Falsifier | Kill |
|---|---|
| `L≈n/2` | combiner/non-LFSR |
| `predict` diverges | taps/width/order wrong |
| `predict` diverges all conv | not a plain LFSR |

## The files

`per-attack-berlekamp-massey/lfsr-*` the attacks · `lfsr-deep`/
`lfsr-catalogue`/`per-family-lfsr*` the family · `edge-cases*` the variants.
