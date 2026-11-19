# crib-drag driver — XOR two same-keystream ciphertexts — case catalogue

tools/crypto_attack.py crib-drag slides your guessed word across the XOR of two ciphertexts and prints every offset where it yields plausible text on both sides.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | --ct1 --ct2 = two ciphertexts under one keystream | the reuse pair | nonce/IV must match |
| 2 | --crib = a guessed plaintext word | the probe | flag{, Content-Type, the, etc. |
| 3 | Output = offsets and revealed counterpart text | candidates | extend the hit bidirectionally |

## Falsifier

Falsifier — no offset ever yields printable on both sides: the keystreams differ (different nonces) or the data is compressed/binary.

## Coverage notes

- The crib must match case and exact bytes — 'flag{' not 'FLAG{'.
- Two printable chars XOR to something non-printable; a hit shows the OTHER side's text, not both.
- Spaces reveal letters via case-flip; run a space crib too.

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
