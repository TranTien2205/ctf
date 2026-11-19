# crib-drag driver — XOR two same-keystream ciphertexts

tools/crypto_attack.py crib-drag slides your guessed word across the XOR of two ciphertexts and prints every offset where it yields plausible text on both sides.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --ct1 --ct2 = two ciphertexts under one keystream | the reuse pair | nonce/IV must match |
| --crib = a guessed plaintext word | the probe | flag{, Content-Type, the, etc. |
| Output = offsets and revealed counterpart text | candidates | extend the hit bidirectionally |

## Steps

1. Collect two ciphertexts sharing a nonce/keystream.
2. python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'.
3. For each reported offset, note what the OTHER message reveals.
4. Iterate: use the newly-recovered text as the next crib and go again.
5. Record the recovered region once it's readable.

## Falsifier

Falsifier — no offset ever yields printable on both sides: the keystreams differ (different nonces) or the data is compressed/binary.

## Traps

- The crib must match case and exact bytes — 'flag{' not 'FLAG{'.
- Two printable chars XOR to something non-printable; a hit shows the OTHER side's text, not both.
- Spaces reveal letters via case-flip; run a space crib too.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib ' the '
```

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
