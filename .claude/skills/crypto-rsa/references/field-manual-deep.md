# Field manual deep — the RSA engagement, the full procedure

## The intake

```python
# extract every integer and key
from Crypto.PublicKey import RSA
import re, json, glob
for f in glob.glob('*'):
    if f.endswith(('.pem','.der','.key','.crt')):
        try:
            k=RSA.importKey(open(f,'rb').read())
            print(f,'n=',k.n.bit_length(),'bits','e=',k.e,'has d:',k.has_private())
        except Exception as ex: print(f,'parse-fail',ex)
    elif f.endswith('.json'):
        d=json.load(open(f)); print(f,'keys:',len(d) if isinstance(d,list) else '?')
    else:
        nums=re.findall(r'\b\d{20,}\b',open(f,errors='replace').read())
        if nums: print(f,'ints:',[int(v).bit_length() for v in nums])
```

Build the sheet: moduli, exponents, ciphertexts, leaks, the keygen.

## The discriminant

```
n count≥2?          → batch-gcd / hastad
2 e on 1 n?          → common-modulus
e ~ n?               → wiener → boneh-durfee
e=3, m short?        → small-e-root
p,q close?           → fermat
p-1 smooth?          → pollard-pm1
p-bits leaked?       → coppersmith
d/phi/dp/p,q held?   → factor-from-d/crt
m2=a·m1+b?           → franklin-reiter
residues/fault?      → crt
```

First yes picks the id.

## The attack order

Cheap first: `fermat`, `batch-gcd`, `common-modulus`, `small-e-root`,
`pollard-pm1`, `wiener` — seconds. Then the lattice: `boneh-durfee`,
`coppersmith`. The applicability bound is the gate — read it before the run.

## The verify

`pow(m,e,n)==c` for `m`; `p*q==n` for `p`,`q`. The only proof.

## The traps (the short list)

- `e=3` ≠ weak — check `m^e<n`.
- balanced primes ≠ close — fermat needs `|p-q|` small in *value*.
- 20 moduli ≠ a bug — a *collision* is.
- a leak in `m` ≠ a leak in `p` — different coppersmith.
- a bound exceeded = negative, not retry.
- a public PEM = `n`,`e` only.

## The record

`solved/<name>/` + `classify_solve.py` + the evidence tuple
`{sheet, attack, bound, recovered, pow}`; or `knowledge/attempts/` for a dead
end with each bound.
