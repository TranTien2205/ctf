# Verify — the only finish line

## The verify step

Every attack returns a candidate scalar `x`/`d`. The proof:

```python
# curve case
from tools.crypto import ec
E = ec.curve(params)
assert E.mul(G, d) == Q            # d·G == Q

# field case
assert pow(g, x, p) == h           # g^x == h
```

`--curve` + `--pubkey` on `hnp-ecdsa` does this inside the tool.

## The flag step

The scalar usually decrypts something or is itself the flag. `flag{…}`/
`CTF{…}` in the decoded output completes the class.

## What verify catches

| Fail | Meaning |
|---|---|
| `d·G ≠ Q` after `ecdsa-nonce-reuse` | `r` wasn't equal, or `z`/`order` wrong |
| `d·G ≠ Q` after `hnp-ecdsa` | too few sigs / wrong bound / nonces fine |
| `g^x ≠ h` after `pohlig-hellman` | wrong `ord(g)` or `h ∉ <g>` |
| `g^x ≠ h` after `bsgs` | `x` outside bound, `h ∉ <g>` |
| `x·P ≠ Q` after smart/singular | not anomalous / not singular |

## The record

`post-probe` with the verify output — the evidence is the verbatim
`x·G == Q` check plus the `flag` in decoded bytes.
