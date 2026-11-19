# Payload dictionary — every command, the flags, the forms

## `lcg-recover`

```bash
python3 tools/crypto_attack.py lcg-recover --outputs o0,o1,o2 --modulus m
```
`m` known + ≥3 raw consecutive outputs → `a`,`c`,`next`.

## `lcg-unknown-modulus`

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,...,o5
```
≥6 raw outputs → `m`,`a`,`c`. NO `--modulus` — it recovers `m`.

## `lcg-truncated`

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,... --modulus m --a a --c c --low-bits b
```
`a`,`c`,`m` + `x>>b` leaks. `--low-bits` = DROPPED bits `b`.

## `berlekamp-massey`

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits 0,1,1,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <hex>
python3 tools/crypto_attack.py berlekamp-massey --bits-file f
```
ONE input form. ≥2·w bits → `(width,taps)`.

## `lfsr-recover`

```bash
python3 tools/crypto_attack.py lfsr-recover --bits b --width w [--taps t]
```
`--width` required; `--taps` optional (BM-derived).

## `lfsr-predict`

```bash
python3 tools/crypto_attack.py lfsr-predict --bits b --taps t --width w --count n
```
`--taps`+`--width` required; `--count` = next bits.

## `mt19937-clone`

```bash
python3 tools/crypto_attack.py mt19937-clone --outputs o0,...,o623 [--count n]
python3 tools/crypto_attack.py mt19937-clone --outputs-file f [--count n]
```
Exactly 624 consecutive raw `getrandbits(32)` words.

## `xorshift128`

```bash
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict n
python3 tools/crypto/xorshift128.py --selftest
```
A standalone `tools/crypto/` module — NOT a `crypto_attack.py` id.

## Common

`--in FILE` (JSON params) · `--json` (compact out) · `--count` (next n).

## Library (import only, no `__main__`)

```python
from tools.crypto import lcg, lfsr, mt19937, xorshift128, numtheory
```
