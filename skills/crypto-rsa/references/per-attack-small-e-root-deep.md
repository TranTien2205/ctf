# per-attack small-e-root / nth-root deep — the wrap, the full treatment

## The mechanism

`c = m^e`, `m^e < n` → `c` a plain integer power → `m = c^{1/e}`.

## Detection

- `e` small (3/5/17/257).
- `m` short — `m^e<n`.
- no pad.
- `c` small — `m^e` may fit a word.

## The bound / falsifier

`m^e < n`. `m^e ≥ n` → wrapped → `hastad`/`coppersmith`.

## The attack

```bash
crypto_attack.py small-e-root --n <n> --e <e> --c <c> [--max-k]
crypto_attack.py nth-root --x <x> --n <n>
```

```python
m, exact = integer_nthroot(c, e); assert exact and pow(m,e)==c  # no mod n
```

## The verify

`pow(m,e)==c` — plain — the wrap never happened.

## Variants

- `nth-root` — the general `e`th root.
- A wrapped `m` → `hastad`/`coppersmith`.

## Failure modes

- `m^e ≥ n` — `c` is a true modular residue.
- A pad — `m` differs → not a root.

## The honest status

Standard — catalogue.
