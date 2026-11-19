# Byte-at-a-time ECB decryption — playbook

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## Ordered playbook

1. Measure block size and secret length: grow input until ciphertext grows; the jump width is the block, the plateau is secret+pad.
2. Hold input = (block-1) bytes; the secret's first byte lands at the block boundary. Store the real ciphertext block.
3. Submit (block-1) bytes + candidate byte; a matching block confirms the byte.
4. Slide the window: input (block-2), guess byte 2 against the known byte-1 context, and so on through the first block.
5. For block N>1, build the guess block from the last 15 recovered bytes; always compare blocks at the same offset.

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/profile?data={PTB}' --bs 16 --resp b64
python3 tools/ecb_oracle.py --url 'https://target/enc' --bs 16 --resp hex --max-requests 20000
```
