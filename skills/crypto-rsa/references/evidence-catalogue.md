# Evidence catalogue — the confirms, the gates, the record

## The confirms

| Claim | The gate | The bytes |
|---|---|---|
| `m` recovered | `pow(m,e,n)==c` | the `pow` output + `long_to_bytes(m)` |
| `p`,`q` recovered | `p*q==n` | `p*q==n` + the `d`/`m` chain |
| `d` recovered | `pow(c,d,n)==m` | `pow` output |
| `phi` recovered | `n-phi+1==p+q` | the consistency + `d`/`m` chain |
| `m_i` (`eth-root`) | `pow(m_i,e,n)==c`+format | the candidate list + `pow` |
| `p` recovered | `1<p<n`,`p|n` | the `gcd`/`divmod` output |

## The record

```bash
RESP="$(python3 - <<'PY'\nprint(pow(m,e,n)==c)\nPY)"
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact --evidence "pow(m,e,n)==c" --response "$RESP"
```

`--evidence` must be a substring of `--response` — the check is verified.

## The decoy

A flag-shaped `m` that fails `pow` — a wrong root/decoy. `p*q` that fails `==n`
— a false split. `d` that doesn't decrypt — wrong.

## The honest status

`pow`/`p*q` is the deterministic gate — the "artifact" for this class. The
files: `evidence-rules.md`,`evidence-rules-deep.md`,`evidence-playbook.md`,
`evidence-catalogue.md`,`verify.md`,`verification-protocol.md`.
