# Edge cases — catalogued oddities

## Empty and tiny inputs

- 0-length input to an ECB oracle: ciphertext is just prefix+pad — reveals
  the fixed-material length.
- Input shorter than one block: no duplicate possible; detection needs ≥
  2×block repeated.

## Blocksize oddities

- DES/3DES: block = 8; every recipe scales (guess windows shrink).
- A 'block cipher' with 1:1 length growth is a stream cipher in disguise —
  re-run detection.

## Partial-length fields

- A 3-byte flag at the end of a token: padding oracle still decrypts it; the
  recovered tail may be all PKCS#7 pad.

## The IV as a separate field

- IV prepended to the ciphertext is the most common packaging: block 0 IS
  the IV; padding-oracle decryption starts at block 1.
- IV in a separate header field: test malleating it independently (IV=key
  and bit-flip targets).

## Double-encoded tokens

- base64(hex(ct)) or hex(base64(ct)): peel every layer before analysis; each
  layer shifts byte positions.

## Weird pad answers

- Service accepts ANY padding as long as it's PKCS#7-parseable: the oracle
  discriminates pad vs MAC, not good pad vs bad pad — still usable, the
  signal just changes polarity.

## Multi-secret ciphertexts

- Several secrets in one blob may use different keys/IVs internally — a
  byte-at-a-time that dies mid-blob may be crossing a key boundary.

## Unicode and length semantics

- A field measured in characters vs bytes: multibyte input shifts block
  alignment differently than the UI suggests. Count bytes.
