# Per-condition map — preconditions and where they're tested

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
