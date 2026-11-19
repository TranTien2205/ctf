# Per-condition map — preconditions and where they're tested — deep

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

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

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

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
