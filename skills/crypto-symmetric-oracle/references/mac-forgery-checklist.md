# MAC and tag forgery — the non-extension routes — operational checklist

When length-extension does not apply, forgery still exists: tag truncation, verification via == (timing compare), unkeyed checksums labeled 'MAC', and key-confusion between verify and sign.

## Checklist

- [ ] Check the compare: submit tags differing only in the first byte and time the reject — early-exit leaks position.
- [ ] Check truncation: send the first k bytes of a valid tag for k = 1..16; the smallest accepted k is the brute-force space.
- [ ] CRC-as-MAC: pick target message, solve for 4 patch bytes that restore the CRC — the checksum is linear.
- [ ] If none fire, the MAC is honest: move to key-recovery paths (leaks, weak keys, PRNG-seeded keys).

## Abort conditions

- Timing attacks on tags need MANY samples per byte — noise swamps a 1ns difference; measure the channel first.
- A truncated tag with only 2-3 accepted bytes is still 16-24 bits of brute force — feasible but bound it first.
- CRC patch bytes go at a position the parser tolerates — usually the end or a length field.

## Falsifier

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.

## Cross-references

`hmac-vs-raw-mac.md` · `length-extension.md` · `authenticated-boundary.md`
