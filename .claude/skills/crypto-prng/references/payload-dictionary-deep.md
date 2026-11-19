# Payload dictionary deep — the commands + when each

## The LCG commands — when

```bash
# m KNOWN, 3+ consecutive raw outputs:
python3 tools/crypto_attack.py lcg-recover --outputs x0,x1,x2 --modulus m

# m UNKNOWN, 6+ consecutive raw outputs:
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,...,o5

# ONLY HIGH BITS leaked (m,a,c known; b low bits dropped):
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,... --modulus m --a a --c c --low-bits b
```

## The LFSR commands — when

```bash
# taps unknown, >=2*w bits:
python3 tools/crypto_attack.py berlekamp-massey --bits b0,b1,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <hex>
python3 tools/crypto_attack.py berlekamp-massey --bits-file bits.txt
# taps+width known, roll forward n:
python3 tools/crypto_attack.py lfsr-predict \
  --bits b --taps t --width w --count n
# taps unknown, reconstruct:
python3 tools/crypto_attack.py lfsr-recover --bits b --width w
```

## The MT command — when

```bash
# 624 consecutive raw getrandbits(32) words:
python3 tools/crypto_attack.py mt19937-clone --outputs o0,...,o623
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt --count 10
```

## The xorshift command — when

```bash
# 4 consecutive 32-bit outputs (xorshift128, not +/64*):
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 5
```

## The `--in FILE` / `--json` forms — when

- `--in FILE` — a JSON object with all params; cleaner for many outputs.
- `--json` — machine-readable output for a downstream step.
