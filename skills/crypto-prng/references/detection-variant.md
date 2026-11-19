# Detection variant — the fingerprint tests, ranked

## The name test — free, highest power

`mt19937`/`mersenne`/`xorshift`/`lfsr`/`shift register`/`lcg`/`linear
congruential`/`rand`/`mt_rand`/`getrandbits`/`nextInt`/`srand`/`seed` —
any of these in source/comments names the generator. If named → skip to
the count gate.

## The output-shape test — free, high power

| Shape | Generator |
|---|---|
| a bitstream (0/1) | LFSR |
| 624+ raw 32-bit words | MT19937 |
| 4+ raw 32-bit words | xorshift/MT |
| mod-`m` ints | LCG |
| floats `[0,1)` | `random()`/`Math.random` variant |
| changes per second | seed-search |

## The LCG test — the difference gcd, cheap

```python
ts = [x[i+1]-x[i] for i in range(len(x)-1)]
m = reduce(gcd, (ts[i+1]*ts[i-1] - ts[i]*ts[i] for i in range(1,len(ts)-1)))
```

- `m` nonzero/stable → affine → LCG.
- `m` → 0/1 → not affine → not an LCG.

## The LFSR test — Berlekamp-Massey

- `L` (linear complexity) convergent & « n → LFSR of width `L`.
- `L ≈ n/2` → combiner/non-LFSR.

## The MT test — the clone attempt

624 raw words → `mt19937-clone` → `predict==held` → MT. The clone IS the
fingerprint — decisive but the costliest.

## The seed test — the window bound

`seed=time()`/`pid`/`srand` in source, or outputs that change
per-second/per-request → bound the window → enumerate → match. The
fingerprint is the seed's form, not the output statistics.

## The low-power tests — don't rely

- uniformity/bit-randomness — no discrimination.
- a single output value — nothing.
- "looks random" — the whole class is that.

## The order

```
name → shape → lcg-gcd (if ints) → BM (if bits) → mt-clone (if 624 words)
→ seed-window (if time/pid) → none match → CSPRNG/keyed → out
```
