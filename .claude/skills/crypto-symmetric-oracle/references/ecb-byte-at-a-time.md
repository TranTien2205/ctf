# Byte-at-a-time ECB decryption

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| You control a prefix position before a hidden secret in the same plaintext | byte-at-a-time applies | alignment then the guess loop |
| Appended secret length measurable by growing input | secret length recoverable | boundary measurement |
| Random prefix before your input | alignment breaks | find the fixed suffix or give up ECB |

## Steps

1. Measure block size and secret length: grow input until ciphertext grows; the jump width is the block, the plateau is secret+pad.
2. Hold input = (block-1) bytes; the secret's first byte lands at the block boundary. Store the real ciphertext block.
3. Submit (block-1) bytes + candidate byte; a matching block confirms the byte.
4. Slide the window: input (block-2), guess byte 2 against the known byte-1 context, and so on through the first block.
5. For block N>1, build the guess block from the last 15 recovered bytes; always compare blocks at the same offset.

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).

## Traps

- Off-by-one at block boundaries: when your input is 0 mod block, the unknown byte is in the NEXT block — track absolute positions, not input length.
- A random per-request prefix defeats the method entirely; detect it by submitting the same input twice and diffing.
- PKCS#7: once you hit the pad region the oracle may reject un-pad-like guesses — stop at the measured secret length.
- tools/ecb_oracle.py drives exactly this loop over HTTP; hand-rolling it means re-sending the prefix alignment yourself.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/profile?data={PTB}' --bs 16 --resp b64
python3 tools/ecb_oracle.py --url 'https://target/enc' --bs 16 --resp hex --max-requests 20000
```

## Cross-references

`ecb-detection.md` · `block-alignment.md` · `tools-ecb-oracle.md`
