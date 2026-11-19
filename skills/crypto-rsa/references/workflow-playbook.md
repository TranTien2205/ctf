# Workflow playbook — the commands, in order

## 0 — the inventory

```bash
python3 tools/crypto_attack.py list        # every id + its bound
```

## 1 — the sheet

```python
# extract n,e,c, the counts, the leak, the keygen tell
```

## 2 — the cheap probes (cost order)

```bash
python3 tools/crypto_attack.py fermat --n <n>
python3 tools/crypto_attack.py batch-gcd --moduli <n1> <n2> ...
python3 tools/crypto_attack.py small-e-root --c <c> --e 3 --n <n>
python3 tools/crypto_attack.py common-modulus --n <n> --e1 <e1> --c1 <c1> --e2 <e2> --c2 <c2>
python3 tools/crypto_attack.py pollard-pm1 --n <n> --b <B>
python3 tools/crypto_attack.py wiener --n <n> --e <e>
```

## 3 — the lattice

```bash
python3 tools/crypto_attack.py boneh-durfee --n <n> --e <e>
python3 tools/crypto_attack.py boneh-durfee-escalate --n <n> --e <e>
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b>
```

## 4 — the terminal recoveries

```bash
python3 tools/crypto_attack.py factor-from-d --n <n> --e <e> --d <d>
python3 tools/crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
python3 tools/crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
python3 tools/crypto_attack.py crt --residues "r1,r2" --moduli "p1,p2"
python3 tools/crypto_attack.py hastad --pairs ... --moduli ... --e <e>
python3 tools/franklin-reiter --n <n> --e <e> --a <a> --b <b> --c1 .. --c2 ..
```

## 5 — the verify

```python
assert pow(m, e, n) == c
assert p * q == n
```

## 6 — the record

```bash
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact \
  --evidence "pow(m,e,n)==c" --response "<the response>"
python3 tools/classify_solve.py --chain <id>   # after a solve
```

## The args

`crypto_attack.py <id> --help` prints the flags for that id — read it before
composing; the flag names differ per attack.
