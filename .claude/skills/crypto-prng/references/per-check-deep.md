# Per-check deep — every gate, the check code, the failure

## The count checks — the code

```python
# lcg-recover — need 3 for a,c
if len(outputs) < 3:
    fail("lcg-recover needs >=3 consecutive raw outputs")

# lcg-unknown-modulus — need 6 for the gcd
if len(outputs) < 6:
    fail("lcg-unknown-modulus needs >=6")

# berlekamp-massey / lfsr — need 2w bits
if len(bits) < 2 * width:
    fail("LFSR needs >=2*width bits")

# mt19937-clone — need exactly 624
if len(outputs) != 624:
    fail("mt19937-clone needs exactly 624")

# xorshift128 — need 4
if len(outputs) < 4:
    fail("xorshift128 needs >=4")
```

## The rawness checks — the code

```python
# every output a raw int — not hex/float/mod
for o in outputs:
    if isinstance(o, float): fail("float — convert to the word pair")
    if isinstance(o, str):   o = int(o, 0)   # decode hex/bin/str
# consecutive — no index gap (checked by collection, not by value)
```

## The invertibility check — `lcg-recover`

```python
from math import gcd
if gcd(outputs[1] - outputs[0], m) != 1:
    fail("x1-x0 non-invertible mod m — gather an odd diff or factor m")
```

## The alignment check

```python
# the outputs are adjacent in the stream — verify by predict
# a shared `random` module injects gaps — detect via predict failure
```

## The seed-window check

```python
assert lo <= issue_epoch <= hi        # the bound exists
assert hi - lo < MAX_ENUMERABLE        # the window is enumerable
```

## The `predict==held` check — the accept

```python
assert predict_next(state) == held_back     # THE gate — never skip
```

## The failure → file map

| Check fails | File |
|---|---|
| count | `boundary-cases*`,`per-boundary*` |
| rawness | `edge-cases*`,`operator-notes*` |
| invertibility | `lcg-recover-deep.md` |
| alignment | `edge-cases*` |
| seed window | `per-family-seed*` |
| `predict!=held` | `falsifiers*`,`verify*` |
