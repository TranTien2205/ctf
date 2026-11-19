# hastad — the broadcast attack, complete

## What it is

The same `m` encrypted for `e` recipients under `e` distinct coprime moduli —
`c_i = m^e mod n_i`. CRT recombines `c_i` into `x = m^e mod ∏ni`; `∏ni > m^e`
→ `x = m^e` exactly → `m = x^{1/e}`.

## The mechanism

`x ≡ c_i mod n_i` (CRT) → `x = m^e mod n1·n2·n3`. `m^e < ∏ni` → `x = m^e` →
`integer_nthroot(x, e) = m`.

## Detection

- **`e` small** (usually 3, up to the recipient count).
- **≥ `e` ciphertexts** of the *same* `m` under `e` coprime `n`.
- **a "broadcast" keygen** — `for n in ns: send(pow(m,e,n))`.

## The bound / falsifier

`≥e` coprime `n`, `∏ni > m^e`, no randomized pad. `<e` n's → `∏ni<m^e` → the
root isn't `m` → dead; route `coppersmith`/`franklin-reiter`. A pad → `m`
differs per `n` → dead.

## The attack

```python
from sympy.ntheory.modular import crt
from sympy import integer_nthroot
x = crt([n1,n2,n3], [c1,c2,c3])[0]
m, ok = integer_nthroot(x, e); assert pow(m,e)==x
```

Or: `crypto_attack.py hastad --pairs c1 c2 c3 --moduli n1 n2 n3 --e 3`.

## The verify

`pow(m,e)==x` — the CRT value equals `m^e`.

## Variants

- **padded broadcast** — `coppersmith` partial-message if the pad is structured.
- **linear relations** — `franklin-reiter` generalises `m_i = a_i·m+b_i`.

## Failure modes

- `<e` recipients — the product is too small.
- A randomized pad (OAEP) — `m` differs per `n` — the whole attack dead.

## The honest status

Standard published attack (Håstad 1988) — catalogue.
