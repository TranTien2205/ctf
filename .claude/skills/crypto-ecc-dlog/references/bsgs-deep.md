# `bsgs` — baby-step giant-step for bounded or small-order DLP

## When it applies

`h = g^x mod p` (or `Q = x·P`) where:

- `x` is bounded (`x < B` for small `B`), or
- the group order is small enough that `√n` is feasible.

Cost: `O(√B)` time and space. Ceiling: ~2⁴⁴ order is the documented limit —
above that the table is too large.

## The command

```bash
python3 tools/crypto_attack.py bsgs --g 2 --h 17 --p 101 --order 100
```

In code (`dlog.bsgs` signature: `max_table=1 << 22` default caps memory):

```python
from tools.crypto import dlog
x = dlog.bsgs(g, h, p, order)          # or max_table=1<<24 to allow more
```

## The math

Write `x = i·m + j` with `m = ⌈√n⌉`:

- baby steps: `g·g^j` for `j = 0..m-1` stored in a table;
- giant steps: `h·(g^{-m})^i` for `i = 0..m-1`, look up in the table.

A collision `h·g^{-im} = g^j` gives `x = im + j`.

## Preconditions

- `ord(g)` ≤ ~2⁴⁴, or `x` bounded below that.
- For a bounded `x < B` use the bound as the effective order.

## Falsifier

No match found → `x` exceeds the bound/order supplied, or `h` isn't in `<g>`.
Re-check `ord(g)`, re-check `h ∈ <g>` (`pow(h, order, p) == 1`), then
consider `pohlig-hellman` (if order is smooth) or a defect curve.

## Common mistakes

- Feeding a 256-bit order — the table will never build; the challenge wants
  PH or a defect attack, not BSGS.
- Forgetting `order` — passing `p` as the bound.
- Confusing `bsgs` bound with a *nonce* bound — BSGS bounds the *secret `x`*,
  HNP bounds the *nonce `k`*. Different problems.
