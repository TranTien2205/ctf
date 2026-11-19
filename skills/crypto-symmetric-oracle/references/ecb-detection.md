# ECB detection — one request, deterministic

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Identical plaintext block appears twice → identical ciphertext block pair | ECB confirmed | byte-at-a-time or cut-and-paste |
| Repeated input never repeats in output | CBC/CTR/stream or ECB+prefix desync | alignment probe |
| Ciphertext length jumps in block-size steps | block cipher (ECB or CBC) | block-size measurement |
| Ciphertext length tracks input 1:1 | stream cipher or CTR | keystream-reuse test |

## Steps

1. Submit 48 identical bytes ('A'*48) — three aligned blocks of a 16-byte cipher.
2. Decode the ciphertext and scan every offset for a duplicated 16-byte window; misalignment still duplicates SOMEWHERE in the stream.
3. Measure block size: grow input one byte at a time; the first length jump is the block size.
4. Locate the block boundary your input controls by binary-searching where the duplicate pair first appears.

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.

## Traps

- A fixed server-side prefix shifts your alignment; the duplicate blocks appear offset by prefix_len mod 16.
- CBC with a fixed IV can mimic ECB on the FIRST block only — check pairs past offset 0.
- Compression before encryption makes 'A'*48 compress to nothing — no duplicate ever appears; that is a different challenge (CRIME-style).
- PKCS#7 padding means a 48-byte aligned input pads to 64 — the pad block is constant too and can be mistaken for signal.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-cut-and-paste.md` · `block-alignment.md`
