# Per-condition map — preconditions and where they're tested — checklist

| Precondition | Test | Holds for |
|---|---|---|
| Chosen plaintext reaches encrypt | submit known bytes, see them in ct | ECB attacks, bit-flip |
| Response discriminates pad vs MAC | two corruptions, two answers | padding oracle |
| Nonce repeats across records | diff captured nonce fields | CTR/GCM reuse |
| Raw MD-hash MAC | source or a successful forge probe | length-extension |
| Fixed IV (or IV=key) | replay determinism / source | CBC IV attacks |
| Tag checked after decrypt | corrupt → crypto error not tag error | malleability attacks |
| Keystream is XOR-based | C1 XOR C2 is structured | crib-drag |
| Secret inside attacker-reachable plaintext | input lands before the secret | byte-at-a-time |
| Token is block-structured | field changes map to block changes | cut-and-paste |
| Early-exit tag compare | timing split per position | verify-oracle timing |
| Truncated tag accepted | shorter tag verifies | truncation forgery |
| Parser survives a garbage block | splice parses | CBC bit-flip |
| Secret length is measurable | grow input, count the plateau | byte-at-a-time |
| The oracle answers at required rate | measure req/s | all loops |
| Unkeyed checksum as 'MAC' | CRC structure in tag | algebraic forgery |

## Checklist

- [ ] check: Chosen plaintext reaches encrypt
- [ ] check: Response discriminates pad vs MAC
- [ ] check: Nonce repeats across records
- [ ] check: Raw MD-hash MAC
- [ ] check: Fixed IV (or IV=key)
- [ ] check: Tag checked after decrypt
- [ ] check: Keystream is XOR-based
- [ ] check: Secret inside attacker-reachable plaintext
- [ ] check: Early-exit tag compare
- [ ] check: Truncated tag accepted
- [ ] check: Parser survives a garbage block
- [ ] check: Secret length is measurable
- [ ] check: The oracle answers at required rate
- [ ] check: Unkeyed checksum as 'MAC'

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
