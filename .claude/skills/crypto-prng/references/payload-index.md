# Payload index — the commands indexed by need

## By family

### LCG

```bash
crypto_attack.py lcg-recover --outputs o --modulus m
crypto_attack.py lcg-unknown-modulus --outputs o
crypto_attack.py lcg-truncated --outputs h --modulus m --a a --c c --low-bits b
```

### LFSR

```bash
crypto_attack.py berlekamp-massey --bits b | --keystream-hex h | --bits-file f
crypto_attack.py lfsr-recover --bits b [--taps t] --width w
crypto_attack.py lfsr-predict --bits b --taps t --width w --count n
```

### MT / xorshift

```bash
crypto_attack.py mt19937-clone --outputs o | --outputs-file f [--count n]
tools/crypto/xorshift128.py --outs o --predict n
```

## By input form

| Have | Flag |
|---|---|
| comma ints | `--outputs`/`--outs`/`--bits` |
| a file | `--outputs-file`/`--bits-file`/`--in` |
| hex | `--keystream-hex` |
| JSON all-params | `--in FILE` |
| machine out | `--json` |

## By need

| Need | Command |
|---|---|
| `a`,`c` from `m` | `lcg-recover --outputs --modulus` |
| `m` from outs | `lcg-unknown-modulus --outputs` |
| state from `x>>b` | `lcg-truncated --low-bits` |
| taps from bits | `berlekamp-massey --bits` |
| register from bits | `lfsr-recover --bits --width` |
| future bits | `lfsr-predict --bits --taps --width --count` |
| clone MT | `mt19937-clone --outputs` |
| predict xorshift | `xorshift128 --outs --predict` |
| enumerate seed | `random.seed(ts)` loop |
