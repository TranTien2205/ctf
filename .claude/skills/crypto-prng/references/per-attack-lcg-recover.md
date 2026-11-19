# Per-attack `lcg-recover` — the card

## Trigger

LCG `x_{i+1} = a·x_i + c mod m` where `m` is known and you hold ≥3
consecutive outputs `x0, x1, x2`.

## Command

```bash
python3 tools/crypto_attack.py lcg-recover --outputs x0,x1,x2 --modulus m
```

## Mechanism

```
a = (x2 - x1)·(x1 - x0)^{-1} mod m
c = x1 - a·x0             mod m
```

Then predict: `next = a·x2 + c mod m`.

## Verify

`predict_next(out) == held_back` — reproduce the next output exactly.

## Falsifiers

- `x1 - x0` not invertible mod `m` (gcd > 1) → more outputs or a different
  `m`.
- `predict != held-back` → `m` wrong, not an LCG, or outputs not
  consecutive/raw.
- Only 2 outputs → can't solve `a`,`c` — need 3.

## Boundaries

- Outputs must be **raw consecutive** — a `mod`/`hex`/`float` between
  state and observation changes `m`'s meaning.
- `x1 - x0` shares a factor with `m` → the inverse doesn't exist → need
  extra outputs or factor `m`.
