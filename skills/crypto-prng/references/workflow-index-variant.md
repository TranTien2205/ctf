# Workflow index variant — the phase table

| Phase | Steps | Files | Command |
|---|---|---|---|
| read | parse+fingerprint | `detection*`,`cipher-id*` | grep, gcd, BM |
| gate | count+raw+window | `boundary*`,`edge-*`,`per-*` | `len`, norm |
| route | pick attack | `decision-table*`,`attack-catalogue` | the tuple |
| solve | run | `payload-*`,`operator-notes*` | `crypto_attack.py <id>` |
| verify | predict==held | `verify*` | `==` |
| record | post-probe/pre-flag | `evidence*` | `tools/hooks.py` |
| escalate | falsifier/rung | `falsifiers*`,`negative-*` | `tools/decide.py` |

## The solve commands

```bash
crypto_attack.py lcg-recover --outputs --modulus
crypto_attack.py lcg-unknown-modulus --outputs
crypto_attack.py lcg-truncated --outputs --modulus --a --c --low-bits
crypto_attack.py berlekamp-massey --bits|--keystream-hex|--bits-file
crypto_attack.py lfsr-recover --bits [--taps] --width
crypto_attack.py lfsr-predict --bits --taps --width --count
crypto_attack.py mt19937-clone --outputs|--outputs-file [--count]
tools/crypto/xorshift128.py --outs --predict
```
