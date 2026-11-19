# rsa-decrypt deep — the terminal plaintext recovery, the full treatment

## The mechanism

`m = c^d mod n` — with `d` (from `factor-from-d` or a leak) or `p`,`q` held.
`crypto_attack.py rsa-decrypt` takes the factors, not `d` — `factor-from-d`
emits `p`,`q`, then `rsa-decrypt --p --q` computes `phi`, `d`, `m` internally.

## Detection

- `d`/`phi`/`dp`/`p`,`q` held — the leak.
- `d` recovered from `wiener`/`boneh-durfee`/`factor-from-d`.

## The attack

```bash
python3 tools/crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
# factor-from-d → p,q → rsa-decrypt --p --q
```

```python
# manual — if you have d directly
m = pow(c, d, n)
assert pow(m, e, n) == c
```

## The chain

`p`,`q` (or `d`) → `phi` → `d` → `m` → `pow` verify → the flag (strip a pad if
`m` is a padded block).

## The verify

`pow(m,e,n)==c` — the only proof. A `m` that fails is a decoy.

## The pad rule

`m` may be a PKCS#1 v1.5 block `\x00\x02<pad>\x00<message>` or OAEP — `pow`
held on the *padded* block; strip to get the flag.

## The honest status

Standard — catalogue.
