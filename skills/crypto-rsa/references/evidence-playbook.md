# Evidence playbook — the confirm commands

## `m` recovered

```python
from Crypto.Util.number import long_to_bytes
assert pow(m, e, n) == c
print(long_to_bytes(m))
```

## `p`,`q` recovered

```python
assert p*q == n and 1 < p < n
phi = (p-1)*(q-1); d = pow(e,-1,phi); m = pow(c,d,n)
assert pow(m, e, n) == c
```

## `d` recovered

```python
m = pow(c, d, n); assert pow(m, e, n) == c
```

## `phi` recovered

```python
assert (n - phi + 1) == p + q    # if p,q known
d = pow(e, -1, phi); m = pow(c, d, n); assert pow(m,e,n)==c
```

## `eth-root` `m_i`

```python
for mi in candidates:
    if pow(mi, e, n) == c and is_flag_format(mi): print(mi)
```

## The hooks call

```bash
RESP="$(python3 - <<'PY'\nprint(pow(m,e,n)==c)\nPY)"
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact --evidence "pow(m,e,n)==c" --response "$RESP"
```

## The rule

`pow`/`p*q` is the gate — a value that fails is a candidate.
