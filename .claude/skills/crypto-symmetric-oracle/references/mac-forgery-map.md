# MAC and tag forgery — the non-extension routes — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Tag verified with == or early-exit compare | timing oracle for the tag | byte-at-a-time tag recovery |
| Tag accepted truncated (first n bytes checked) | truncation forgery | brute the checked prefix |
| CRC32/CRC16 used as a 'MAC' | linear checksum — algebraically forgeable | solve for the patch bytes |
| Same key signs and verifies on different algorithms | key confusion (RS/HS-style) | reuse a public value as the HMAC key |

## Falsifier

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.
