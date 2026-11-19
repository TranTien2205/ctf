# Falsifiers — the observations that close each attack

Every attack in this class has a specific observation that kills it. Check
the falsifier before investing a loop; the falsifier is cheaper than the
attack.

## Class-level

The mode is authenticated before decryption: GCM tag, encrypt-then-MAC, or
any check that rejects a tampered ciphertext identically for every corruption.
No malleability oracle exists. What remains: nonce reuse, key material, or
reclassification.

## Per-attack

| Attack | Falsifier |
|---|---|
| ECB fingerprint | no duplicated block in a 48-byte repeated input |
| Byte-at-a-time | recovered bytes stop being coherent mid-loop |
| Cut-and-paste | token carries MAC over whole ciphertext |
| CBC padding oracle | all corruptions → identical response incl. timing |
| CBC bit-flip | token authenticated, or parser rejects garbage block |
| CTR/keystream reuse | every nonce distinct across captures |
| Crib-drag | no offset yields printable on both sides under any crib |
| GCM nonce reuse | no reused nonce in captures |
| Length extension | forged MAC rejected at all secret lengths |
| Single-byte XOR | no key gives mostly-printable output |
| HMAC/verify timing | distributions overlap at 200+ samples |

## Using falsifiers

1. Run the cheapest falsifier probe FIRST (usually one request or one grep).
2. If it fires, record the negative and route out — do not start the loop.
3. If it does not fire, the attack applies; run it.
4. A falsifier that fires mid-loop means the mechanism was misread — stop,
   re-identify, don't tune parameters.
