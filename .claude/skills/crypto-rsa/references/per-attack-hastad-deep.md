# per-attack hastad deep — the broadcast, the full treatment

## The mechanism

The same `m` to `e` recipients under `e` coprime `n` — `c_i = m^e mod n_i`.
CRT recombines `c_i` → `x = m^e mod ∏ni`; `∏ni > m^e` → `x = m^e` → `m=x^{1/e}`.

## Detection

- `e` small (3, up to the recipient count).
- `≥e` ciphertexts of the same `m` under `e` coprime `n`.
- a "broadcast" keygen — `for n in ns: send(pow(m,e,n))`.

## The bound / falsifier

`≥e` coprime `n`, `∏ni > m^e`, no pad. `<e`/`∏ni<m^e`/pad → dead.

## The attack

```bash
crypto_attack.py hastad --pairs "n1,c1;n2,c2;n3,c3" --e 3    # or --n --c
```

```python
x = crt(ns, cs)[0]; m,ok = integer_nthroot(x, e); assert pow(m,e)==x
```

## The verify

`pow(m,e)==x` — `x = m^e` exactly.

## Variants

- A padded broadcast → `coppersmith` partial-message.
- Linear relations → `franklin-reiter` generalises `m_i=a_i·m+b_i`.

## Failure modes

- `<e` recipients — `∏ni<m^e`.
- A randomized pad — `m` differs per `n`.

## The honest status

Håstad 1988 — catalogue.
