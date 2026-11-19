# MAC and tag forgery — the non-extension routes — playbook

When length-extension does not apply, forgery still exists: tag truncation, verification via == (timing compare), unkeyed checksums labeled 'MAC', and key-confusion between verify and sign.

## Ordered playbook

1. Check the compare: submit tags differing only in the first byte and time the reject — early-exit leaks position.
2. Check truncation: send the first k bytes of a valid tag for k = 1..16; the smallest accepted k is the brute-force space.
3. CRC-as-MAC: pick target message, solve for 4 patch bytes that restore the CRC — the checksum is linear.
4. If none fire, the MAC is honest: move to key-recovery paths (leaks, weak keys, PRNG-seeded keys).

## Falsifier

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.

## Commands

```bash
python3 tools/crypto_attack.py list
```
