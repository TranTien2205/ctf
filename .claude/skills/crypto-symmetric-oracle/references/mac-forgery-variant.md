# MAC and tag forgery — the non-extension routes — surface variants

When length-extension does not apply, forgery still exists: tag truncation, verification via == (timing compare), unkeyed checksums labeled 'MAC', and key-confusion between verify and sign.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| Tag verified with == or early-exit compare | timing oracle for the tag | byte-at-a-time tag recovery |
| Tag accepted truncated (first n bytes checked) | truncation forgery | brute the checked prefix |
| CRC32/CRC16 used as a 'MAC' | linear checksum — algebraically forgeable | solve for the patch bytes |
| Same key signs and verifies on different algorithms | key confusion (RS/HS-style) | reuse a public value as the HMAC key |

## Variant-specific traps

- Timing attacks on tags need MANY samples per byte — noise swamps a 1ns difference; measure the channel first.
- A truncated tag with only 2-3 accepted bytes is still 16-24 bits of brute force — feasible but bound it first.
- CRC patch bytes go at a position the parser tolerates — usually the end or a length field.

## Falsifier

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.

## Cross-references

`hmac-vs-raw-mac.md` · `length-extension.md` · `authenticated-boundary.md`
