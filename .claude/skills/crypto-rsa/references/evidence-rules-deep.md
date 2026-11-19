# Evidence rules deep — the standard, the chain, the record

## The standard

`EVIDENCE_POLICY.md` — a flag counts only from a live response or a supplied
artifact. For RSA the "artifact" *is* the identity check — a deterministic
`pow`/`gcd`/`mul` on the recovered value. A value that fails is a candidate; an
attack that ran is not proof.

## The proof chain, per type

### Plaintext recovery
```
m (recovered)
  → pow(m, e, n) == c         ← the cryptographic gate
  → long_to_bytes(m)          ← the content (strip a pad)
  → the flag bytes appear in the artifact
```
`pow(m,e,n)==c` is the *cryptographic* confirm — it asserts `m` is the unique
decryption. The flag-shaped bytes are the *content* confirm — they assert the
plaintext is the flag. Both.

### Factor recovery
```
p, q (recovered)
  → p * q == n                ← the gate
  → 1 < p < n, p prime        ← sanity
  → phi = (p-1)(q-1); d = inverse(e, phi)
  → m = pow(c, d, n); pow(m, e, n) == c
```
`p*q==n` proves the factor; the `d`→`m`→`pow` chain completes the decryption.

### d recovery
```
d (recovered)
  → m = pow(c, d, n)
  → pow(m, e, n) == c         ← the gate
```
A `d` that decrypts `c` to `m` and re-encrypts to `c` is proven.

### phi recovery
```
phi (given/recovered)
  → n - phi + 1 == p + q      ← consistency
  → d = inverse(e, phi); m = pow(c,d,n); pow(m,e,n)==c
```

### The negative proof
```
bound exceeded (the falsifier observed)
  → record in negative-results / knowledge/attempts
  → the attack is closed for this challenge
```
A measured negative is evidence too — it closes a layer.

## The decoy rule

A flag-shaped string that fails `pow` is a candidate, never a flag. A `m` that
decrypts to garbage is a wrong root (`eth-root` — try the others) or a wrong
`d`. The gate is the identity, not the shape.

## The hooks call

```bash
RESP="$(python3 - <<'PY'\nprint(pow(m,e,n)==c)\nPY)"
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact \
  --evidence "pow(m,e,n)==c" --response "$RESP"
```

`--evidence` must be a substring of `--response` — the `pow` output is the
bytes the evidence was read from.
