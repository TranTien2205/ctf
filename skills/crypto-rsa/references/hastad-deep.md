# hastad deep — the broadcast attack, the full treatment

## The mechanism

The same `m` encrypted for `e` recipients under `e` distinct coprime moduli —
`c_i = m^e mod n_i`. CRT recombines `c_i` into `x = m^e mod ∏ni`; `∏ni > m^e`
→ `x = m^e` exactly → `m = x^{1/e}`.

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

Or: `crypto_attack.py hastad --pairs "n1,c1;n2,c2;n3,c3" --e 3` /
`--n/--c` lists.

## The chain

`x` → `m` → `pow(m,e)==x` → the flag (strip a pad if `m` is a padded block).

## The verify

`pow(m,e)==x` — the CRT value equals `m^e` exactly.

## Worked shape

```
c1 = m³ mod n1, c2 = m³ mod n2, c3 = m³ mod n3   (same m, 3 coprime n)
x = CRT(c1,c2,c3) = m³ mod n1n2n3
m³ < n1n2n3 → x = m³ → m = x^{1/3}
```

## Variants

- **padded broadcast** — `coppersmith` partial-message if the pad is structured.
- **linear relations** — `franklin-reiter` generalises `m_i = a_i·m+b_i`.
- **`e` larger** — needs `e` moduli, not 3 — `c` count must match.

## Failure modes

- `<e` recipients — the product is too small.
- A randomized pad (OAEP) — `m` differs per `n` — the whole attack dead.

## The honest status

Håstad 1988 — catalogue.
