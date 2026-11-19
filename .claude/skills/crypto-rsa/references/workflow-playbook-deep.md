# Workflow playbook deep — the commands, in order, annotated

## 0 — the inventory

```bash
python3 tools/crypto_attack.py list        # every id + its applicability bound
python3 tools/crypto_attack.py <id> --help # the exact flags for <id>
```

`list` reports `lll_backend` — `fpylll` absent → a pure-python LLL, slower.

## 1 — the sheet

```python
# extract n,e,c, the counts, the leak, the keygen tell
from Crypto.PublicKey import RSA
import re, json, glob
for f in glob.glob('*'):
    if f.endswith(('.pem','.der','.key','.crt')):
        k = RSA.importKey(open(f,'rb').read())
        print(f, k.n.bit_length(), k.e, k.has_private())
```

Fill `parameter-sheet.md`: `n`,`e`,`c` counts; `e_sig`; the leak; `keygen`;
`degenerate`.

## 2 — the cheap probes (cost order)

```bash
crypto_attack.py fermat --n <n> --max-iters <K>
crypto_attack.py batch-gcd --moduli n1 n2 ...
crypto_attack.py small-e-root --n --e --c --max-k
crypto_attack.py common-modulus --n --e1 --c1 --e2 --c2
crypto_attack.py pollard-pm1 --n --b
crypto_attack.py wiener --n --e
crypto_attack.py crt --residues "r1,r2" --moduli "p1,p2"
crypto_attack.py hastad --pairs "n1,c1;n2,c2" --e <e>
crypto_attack.py factor-from-d --n --e --d
crypto_attack.py rsa-decrypt --n --e --c --p --q
crypto_attack.py eth-root --c --e --factors "<p>,<q>"
```

## 3 — the lattice

```bash
crypto_attack.py boneh-durfee --n --e --delta --m --t
crypto_attack.py boneh-durfee-escalate --n --e --m --t
crypto_attack.py coppersmith-high-bits --n --known --bits --p-bits --m --t
crypto_attack.py coppersmith-core --n --a --X --m --t
```

## 4 — the manual attacks (no `crypto_attack.py` id)

```python
# franklin-reiter — gcd of x^e-c1 and (ax+b)^e-c2 in Z_n[x] → x-m
# crt Bellcore — gcd(pow(sig_faulty,e,n)-m, n) → q
# crt dp — for k in 1..e: p=(e*dp-1)/k+1; if n%p==0 → p
```

## 5 — the verify

```python
assert pow(m, e, n) == c    # plaintext
assert p * q == n           # factor
```

## 6 — the record

```bash
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact --evidence "pow(m,e,n)==c" --response "<resp>"
python3 tools/classify_solve.py --chain <id>   # after a solve
```
