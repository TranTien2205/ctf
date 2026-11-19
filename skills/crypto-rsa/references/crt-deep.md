# crt deep — residues, CRT-RSA, and the Bellcore fault

## Three preconditions

1. **Residues**: `m ≡ ri (mod pi)` for several small coprime `pi` — combine to
   `m mod ∏pi`; if `∏pi > m`, `m` is recovered.
2. **CRT-RSA leak**: `dp`,`dq`,`qInv` (the fast-decryption params) leak →
   reconstruct the private key.
3. **Bellcore fault**: a correct `s` and a faulty `s'` of the same `m` →
   `gcd(s'^e - m, n) = q` (or `p`).

## The maths

### Residue recovery
CRT: `x ≡ ri mod pi` for `i=1..k`, `∏pi` coprime → unique `x mod ∏pi`. If
`∏pi > m`, `x = m`.

### CRT-RSA
`mp = c^dp mod p`, `mq = c^dq mod q`, `m = mp + q·((qInv·(mp-mq)) mod p)` or the
symmetric form. A leaked `dp` alone: `e·dp - 1` is a multiple of `p-1` →
`gcd(a^(e·dp-1)-1, n) = p`.

### Bellcore
A fault in `mp` makes `s'` valid mod `q` but not `p`: `s'^e ≡ m mod q`,
`s'^e ≢ m mod p` → `gcd(s'^e - m, n) = q`. Needs a correct `s` *and* a faulty
`s'` of the same `m`.

## The tool

```bash
python3 tools/crypto_attack.py crt --residues "r1,r2,...;p1,p2,..."
```

## The bound / falsifier

- Residues: `∏pi > m` required.
- Bellcore: a fault + a correct sig of the same `m`.
- `dp`,`dq`,`qInv` must be consistent with `n`.

## The verify

`pow(m,e,n)==c`, or `p*q==n` for a recovered factor.

## The traps

- Bellcore needs the **faulty** signature — a correct `s` alone is not enough;
  the challenge must inject the fault.
- A single `dp` (not `dq` too) still factors `n` via the `e·dp-1` gcd.
- The CRT-RSA private-key PEM carries `dp`,`dq`,`qInv` as fields — a "partially
  redacted private key" leaks them.
