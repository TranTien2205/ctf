# Parameter sheet — fill this before any attack

## The sheet

```python
# crypto-rsa parameter sheet — copy and fill
n_list   = [...]    # every modulus
e_list   = [...]    # every exponent
c_list   = [...]    # every ciphertext
m_known  = [...]    # any plaintext / partial plaintext
p_hint   = None     # leaked p bits / a centred guess
d_hint   = None     # d / phi / dp / dq / qInv
e_sig    = None     # 'small' | 'default' | 'large' | 'gcd-issue'
n_size   = n.bit_length()
relation = None     # m2 = a*m1+b, residues, a fault
keygen   = ''       # the tell from the generator
degenerate = None   # n square / prime / smooth / multi-prime
```

## The discriminators, derived

```python
from math import gcd
import sympy
# counts
print('n count:', len(set(n_list)), 'e count:', len(set(e_list)), 'c count:', len(c_list))
# e signature
for n,e in zip(n_list,e_list):
    bl = n.bit_length()
    print(f'n={bl}b e={e}', '->', 'e~n (small-d)' if e.bit_length()>0.9*bl else 'small-e' if e in(3,5,17,257) else 'default')
# degenerate
if sympy.isprime(n): print('n is PRIME')
if isqrt(n)**2==n: print('n is a SQUARE')
# gcd(e,phi) if p,q known
```

## The routing fields

| Field | If set → |
|---|---|
| `n_list` len ≥ 2 | `batch-gcd`/`hastad` |
| `e_list` len 2, same `n` | `common-modulus` |
| `c_list` len ≥ e | `hastad` |
| `e_sig`='large' | `wiener`/`boneh-durfee` |
| `e_sig`='small' | `small-e`/`hastad`/`franklin-reiter` |
| `e_sig`='gcd-issue' | `eth-root` |
| `d_hint`/`p`/`q` set | `factor-from-d`/`crt`/`rsa-decrypt` |
| `p_hint` set | `coppersmith-*` |
| `relation`='linear' | `franklin-reiter` |
| `relation`='residues/fault' | `crt` |
| `keygen`='next_prime/close' | `fermat` |
| `keygen`='smooth p-1' | `pollard-pm1` |
| `degenerate` set | the degenerate `phi` |
