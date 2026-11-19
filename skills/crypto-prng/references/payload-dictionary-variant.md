# Payload dictionary variant — the commands, compact

## LCG

```bash
crypto_attack.py lcg-recover --outputs o --modulus m
crypto_attack.py lcg-unknown-modulus --outputs o
crypto_attack.py lcg-truncated --outputs h --modulus m --a a --c c --low-bits b
```

## LFSR

```bash
crypto_attack.py berlekamp-massey --bits b | --keystream-hex h | --bits-file f
crypto_attack.py lfsr-predict --bits b --taps t --width w --count n
crypto_attack.py lfsr-recover --bits b [--taps t] --width w
```

## MT / xorshift

```bash
crypto_attack.py mt19937-clone --outputs o | --outputs-file f [--count n]
tools/crypto/xorshift128.py --outs o --predict n [--selftest]
```

## Common

```
--in FILE  JSON params   --json  compact out   --count n  next-outputs
```

## The library (no __main__)

```python
from tools.crypto import lcg, lfsr, mt19937, xorshift128
```
