# MAC and tag forgery — the non-extension routes — summary

When length-extension does not apply, forgery still exists: tag truncation, verification via == (timing compare), unkeyed checksums labeled 'MAC', and key-confusion between verify and sign.

## Signal → route

- Tag verified with == or early-exit compare → byte-at-a-time tag recovery
- Tag accepted truncated (first n bytes checked) → brute the checked prefix
- CRC32/CRC16 used as a 'MAC' → solve for the patch bytes
- Same key signs and verifies on different algorithms → reuse a public value as the HMAC key

## Falsifier

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.
