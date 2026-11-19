# Worked examples full — the complete walkthroughs, command by command

## Solve 1 — `q=next_prime(p)` → `fermat` → `rsa-decrypt`

```python
# chal.py — the tell
p = getPrime(512); q = next_prime(p); n = p*q; e = 65537
c = pow(m, e, n)
# handout: n, e, c
```

The discriminator: `next_prime` — `|p-q|` is a few hundred. `fermat` climbs
`a=(p+q)/2` from `√n` in `O(|p-q|)` steps.

```bash
python3 tools/crypto_attack.py fermat --n <n> --max-iters 1000000
# → p = ..., q = ...
```

```python
assert p*q == n                          # the factor gate
from Crypto.Util.number import long_to_bytes
phi = (p-1)*(q-1); d = pow(e,-1,phi); m = pow(c,d,n)
assert pow(m,e,n) == c                   # the plaintext gate
print(long_to_bytes(m))                  # the flag bytes
```

Or the one-shot chain: `fermat --n` → `rsa-decrypt --n --e --c --p --q`.

## Solve 2 — `e=3`, `m³<n` → `small-e-root`

```python
# chal.py
e = 3; m = bytes_to_long(b"flag{short}"); c = pow(m,3,n)   # m³ < n
```

`m` ≈ 88 bits → `m³` ≈ 264 bits < `n` (2048) → `c = m³` exactly.

```bash
python3 tools/crypto_attack.py small-e-root --n <n> --e 3 --c <c>
# → m
```

```python
m, exact = integer_nthroot(c, 3); assert exact and pow(m,3) == c  # no mod n
print(long_to_bytes(m))                # flag{short}
```

## Solve 3 — `e`≈`n`, `d` small → `wiener` → `d` → `m`

```python
# chal.py — 'fast decryption'
d = getPrime(64); e = inverse(d, phi); c = pow(m,e,n)   # e ≈ n
```

`e` ~2048 bits — a small `d`. `d=64<n^0.25=512` → Wiener's CF.

```bash
python3 tools/crypto_attack.py wiener --n <n> --e <e>   # → d
```

```python
m = pow(c, d, n); assert pow(m,e,n)==c
```

If `wiener` no-find → `boneh-durfee --n --e` → `boneh-durfee-escalate --m --t`.

## Solve 4 — a `.json` of `n` → `batch-gcd`

```json
[{"n": ...,"e":65537}, ..., 50 entries]
```

```bash
python3 tools/crypto_attack.py batch-gcd --file keys.json   # → (i,j,p)
```

```python
q = ns[i]//p; assert p*q==ns[i]
phi=(p-1)*(q-1); d=pow(e,-1,phi); m=pow(c,d,ns[i]); assert pow(m,e,ns[i])==c
```

## Solve 5 — broadcast `m`, `e=3` → `hastad`

```python
for i in range(3): send(pow(m,3,n_i))   # same m, 3 coprime n
```

```bash
python3 tools/crypto_attack.py hastad --pairs "n1,c1;n2,c2;n3,c3" --e 3   # → m
```

```python
x = crt([n1,n2,n3],[c1,c2,c3])[0]; m,ok = integer_nthroot(x,3); assert pow(m,3)==x
```

## Solve 6 — `p` high bits → `coppersmith-high-bits`

```python
# p_high leaked — top 256 bits of p
a = p_high << 256
```

```bash
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits 256
# → x; p = a+x; p|n → q → phi → d → m → pow
```

## Solve 7 — `d`/`phi` held → `factor-from-d` → `rsa-decrypt`

```bash
python3 tools/crypto_attack.py factor-from-d --n <n> --e <e> --d <d>   # → p,q
python3 tools/crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
```

## Solve 8 — `gcd(e,phi)=2` → `eth-root`

```bash
python3 tools/crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
# → the g candidates; pow(m_i,e,n)==c + format → the true m
```

## The verify, always

`pow(m,e,n)==c` / `p*q==n` — run them.
