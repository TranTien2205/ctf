# crib-drag driver — XOR two same-keystream ciphertexts — operational checklist

tools/crypto_attack.py crib-drag slides your guessed word across the XOR of two ciphertexts and prints every offset where it yields plausible text on both sides.

## Checklist

- [ ] Collect two ciphertexts sharing a nonce/keystream.
- [ ] python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'.
- [ ] For each reported offset, note what the OTHER message reveals.
- [ ] Iterate: use the newly-recovered text as the next crib and go again.
- [ ] Record the recovered region once it's readable.

## Abort conditions

- The crib must match case and exact bytes — 'flag{' not 'FLAG{'.
- Two printable chars XOR to something non-printable; a hit shows the OTHER side's text, not both.
- Spaces reveal letters via case-flip; run a space crib too.

## Falsifier

Falsifier — no offset ever yields printable on both sides: the keystreams differ (different nonces) or the data is compressed/binary.

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
