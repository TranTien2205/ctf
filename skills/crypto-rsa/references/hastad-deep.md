# hastad deep — the broadcast attack, in full

## The precondition

The **same** plaintext `m` encrypted to `e` different recipients under `e`
different moduli `n1…ne`, all with the same small `e`. You hold `c1…ce`.

## The maths

`ci = m^e mod ni`. By CRT, the system `x ≡ ci (mod ni)` has a unique solution
`x mod N` for `N = ∏ni`. Since `x ≡ m^e mod ni` for every `i`, `x ≡ m^e mod N`.
When `N > m^e`, `x = m^e` as a plain integer — take the `e`-th root.

With `e=3` and 3 moduli of ~1024 bits, `N ~ 3072` bits > `m³ ~ 2400` bits for a
100-byte flag — the root recovers `m`.

## The procedure

```python
from sympy.ntheory.modular import crt
from sympy import integer_nthroot
x = crt([n1,n2,n3],[c1,c2,c3])[0]      # x = m^e mod N
m, exact = integer_nthroot(x, e)
assert exact and pow(m, e) == x
```

## The tool

```bash
python3 tools/crypto_attack.py hastad --pairs "n1,c1;n2,c2;n3,c3" --e <e>
python3 tools/crypto_attack.py crt --residues "c1,c2,c3;n1,n2,n3"
```

## The bound / falsifier

- `≥ e` ciphertexts of the **same** `m` under distinct coprime `n`.
- `< e` → `N < m^e` → root isn't `m` → route to `coppersmith`/pad/`franklin`.
- Pad randomizes `m` → no common root → dead.
- Shared prime → `batch-gcd` anyway.

## The verify

`pow(m,e)==x` exactly; `pow(m,e,ni)==ci` per modulus.

## The traps

- **Same `m` is the gate** — a random pad means each `mi` differs; the count is
  right but the attack is dead.
- `N = ∏ni` must exceed `m^e` — a borderline case may root to `m` plus a wrap;
  verify with `pow`.
- The `e` in the bound is the *exponent* — 3 recipients for `e=3`, 17 for `e=17`.
