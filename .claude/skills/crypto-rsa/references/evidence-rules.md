# Evidence rules — the standard

`EVIDENCE_POLICY.md` — a flag counts from a live response or a supplied artifact.
For RSA the artifact *is* the identity check:

- `pow(m,e,n)==c` — a plaintext recovery.
- `p*q==n` — a factor recovery.
- `pow(c,d,n)==m` + `pow(m,e,n)==c` — a `d` recovery.
- `n-phi+1==p+q` — a `phi` consistency.
- `gcd` between `1` and `n` — a non-trivial factor.

## Not evidence

- a flag-shaped string that fails `pow` — a decoy.
- an attack that "ran" — exit status.
- a bound "close to" exceeded — binary.
- a plausible `d`/`phi` that fails `pow`/`p*q` — wrong input.

## The hooks call

```bash
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact \
  --evidence "pow(m,e,n)==c" --response "<the pow output>"
```

`--evidence` must be a substring of `--response`. See `evidence-deep.md`,
`evidence-catalogue.md`, `evidence-map.md`, `evidence-playbook.md`.
