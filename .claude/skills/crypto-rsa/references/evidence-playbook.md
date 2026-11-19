# Evidence playbook — the proof, run as commands

## The plaintext proof

```python
# recovered m
assert pow(m, e, n) == c, "candidate, not a recovery"
```

## The factor proof

```python
# recovered p,q
assert p * q == n
assert 1 < p < n
phi = (p-1)*(q-1); d = pow(e,-1,phi)
assert pow(c, d, n) == m
```

## The d proof

```python
# recovered d
m = pow(c, d, n)
assert pow(m, e, n) == c
```

## The eth-root proof

```python
for m in eth_root_candidates(c, e, n, p, q):
    if pow(m, e, n) == c and isprintable(m): print('FLAG', m)
```

`pow` picks the true root; the format confirms.

## The padded-plaintext proof

```python
b = long_to_bytes(m)
# PKCS#1 v1.5:  \x00\x02<padding>\x00<message>
# strip to the flag; pow(m,e,n)==c held on the padded block
```

## The hooks call

```bash
RESP="$(python3 -c 'print(pow(m,e,n)==c)')"
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact \
  --evidence "pow(m,e,n)==c" --response "$RESP"
```

## What fails

- `pow!=c` → a candidate.
- `p*q!=n` → not a factor.
- a flag-shaped string without `pow` → a decoy.
- exit status → not evidence.
