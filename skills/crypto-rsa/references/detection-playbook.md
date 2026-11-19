# Detection playbook — the fingerprint, run as commands

## Step 1 — parse everything

```python
from Crypto.PublicKey import RSA
import re, json, glob, os

for f in sorted(glob.glob('*')):
    lo = f.lower()
    try:
        if lo.endswith(('.pem','.der','.key','.crt','.pub')):
            k = RSA.importKey(open(f,'rb').read())
            print(f, '| n:', k.n.bit_length(), 'bits | e:', k.e,
                  '| private:', k.has_private())
            if k.has_private():
                print('   d bits:', k.d.bit_length(),
                      'p:',k.p is not None,'q:',k.q is not None,
                      'dp:',getattr(k,'dp',None) is not None)
        elif lo.endswith('.json'):
            d = json.load(open(f))
            n_list = d if isinstance(d,list) else [d]
            print(f, '| entries:', len(n_list))
        else:
            ints = [int(v) for v in re.findall(r'\b\d{20,}\b', open(f,errors='replace').read())]
            if ints: print(f, '| ints:', [i.bit_length() for i in ints])
    except Exception as ex:
        print(f, '| parse-fail:', ex)
```

## Step 2 — the count table

```python
# fill the sheet
n_count = ...   # moduli
e_count = ...   # exponents
c_count = ...   # ciphertexts
leaks   = [...] # d, phi, dp, dq, qInv, p_bits, m_partial, fault
```

## Step 3 — the e-signature

```python
if e == 65537:      family = 'default — look elsewhere'
elif e in (3,5,17): family = 'small-e — small-e-root / hastad / franklin-reiter'
elif e.bit_length() > 0.9*n.bit_length(): family = 'e~n — wiener / boneh-durfee'
```

## Step 4 — the keygen tell

Read the generator. One line names the bug:
- `next_prime`/`p+k` → fermat
- `getPrime(small)` for `d` → wiener/boneh-durfee
- `random.seed` → batch-gcd
- `p-1` smooth → pollard
- `e=3`,no pad → small-e/hastad
- `a*m1+b` → franklin-reiter
- `dp`,`dq`,`qInv` → crt

## Step 5 — the discriminator

`attack-table.md` — first yes picks the id. `per-bound.md` — the falsifier.
