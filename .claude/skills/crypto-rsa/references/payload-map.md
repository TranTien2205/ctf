# Payload map — the attack id → the command shape → the flags

## The invocation shape

```
python3 tools/crypto_attack.py <attack-id> <flags>
```

`<id> --help` prints that attack's flags. The common flags: `--n`, `--e`, `--c`,
`--moduli`, `--pairs`, `--d`, `--phi`, `--p`, `--q`, `--dp`, `--a`, `--b`,
`--b`, `--known`, `--bits`, `--residues`, `--e1`,`--e2`,`--c1`,`--c2`.

## By attack id

| id | The flags it needs |
|---|---|
| `batch-gcd` | `--moduli n1 n2 ...` |
| `common-modulus` | `--n --e1 --c1 --e2 --c2` |
| `fermat` | `--n` |
| `wiener` | `--n --e` |
| `boneh-durfee` / `-escalate` | `--n --e` |
| `coppersmith-high-bits` | `--n --known <a> --bits <b>` |
| `coppersmith-core` | `--n --a <a> --X <bound>` |
| `small-e-root` / `nth-root` | `--c --e --n` |
| `hastad` | `--pairs ... --moduli ... --e` |
| `pollard-pm1` | `--n --b` |
| `franklin-reiter` | `--n --e --a --b --c1 --c2` |
| `crt` | `--residues "r1,r2" --moduli "p1,p2"` / `--n --e --sig --sig-faulty` / `--dp --e --n` |
| `factor-from-d` | `--n --e --d` / `--n --phi` |
| `rsa-decrypt` | `--n --e --d --c` / `--n --p --q --e --c` |
| `eth-root` | `--c --e --n --p --q` |

## The payload semantics

The "payload" is the *integer arguments*, not a string to inject — `n`,`e`,`c`,
`p`,`q`,`d`,`phi`,`dp`,`a`,`b`,`B`,the residues. Build them on the
`parameter-sheet` first; pass them on the command line or in a driver script.

## The verify payload

```python
assert pow(m, e, n) == c   # plaintext
assert p * q == n          # factor
```
