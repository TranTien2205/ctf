# Per-check — every gate → the code

## The count checks

```python
# lcg-recover
assert len(outputs) >= 3
# lcg-unknown-modulus
assert len(outputs) >= 6
# berlekamp-massey / lfsr
assert len(bits) >= 2 * width
# mt19937-clone
assert len(outputs) == 624
# xorshift128
assert len(outputs) >= 4
```

## The rawness checks

```python
# consecutive — no index gap
# raw — ints, not hex/float/mod
outputs = [int(h, 16) if isinstance(h, str) else h for h in outputs]
```

## The invertibility check (lcg-recover)

```python
from math import gcd
assert gcd(outputs[1] - outputs[0], m) == 1   # else a's inverse is missing
```

## The `predict == held-back` check

```python
assert predict_next(state) == held_back
```

## The seed-window check

```python
assert lo <= seed_bound <= hi   # the epoch is bounded
```

## The files

`per-check-deep.md` — annotated; `detection-checklist*.md` — the run-list;
`operator-notes*.md` — the helpers.
