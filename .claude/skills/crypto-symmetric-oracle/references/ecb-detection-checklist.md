# ECB detection — one request, deterministic — operational checklist

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## Checklist

- [ ] Submit 48 identical bytes ('A'*48) — three aligned blocks of a 16-byte cipher.
- [ ] Decode the ciphertext and scan every offset for a duplicated 16-byte window; misalignment still duplicates SOMEWHERE in the stream.
- [ ] Measure block size: grow input one byte at a time; the first length jump is the block size.
- [ ] Locate the block boundary your input controls by binary-searching where the duplicate pair first appears.

## Abort conditions

- A fixed server-side prefix shifts your alignment; the duplicate blocks appear offset by prefix_len mod 16.
- CBC with a fixed IV can mimic ECB on the FIRST block only — check pairs past offset 0.
- Compression before encryption makes 'A'*48 compress to nothing — no duplicate ever appears; that is a different challenge (CRIME-style).

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-cut-and-paste.md` · `block-alignment.md`
