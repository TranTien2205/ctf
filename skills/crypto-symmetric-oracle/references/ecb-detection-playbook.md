# ECB detection — one request, deterministic — playbook

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## Ordered playbook

1. Submit 48 identical bytes ('A'*48) — three aligned blocks of a 16-byte cipher.
2. Decode the ciphertext and scan every offset for a duplicated 16-byte window; misalignment still duplicates SOMEWHERE in the stream.
3. Measure block size: grow input one byte at a time; the first length jump is the block size.
4. Locate the block boundary your input controls by binary-searching where the duplicate pair first appears.

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
python3 tools/ecb_oracle.py --selftest
```
