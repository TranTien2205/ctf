# Detection — naming the oracle in ≤5 requests

The discriminator runs once, before any exploit. Five probes, each cheap,
each ruling out a branch.

## Probe order

1. **Replay** — same input twice. Identical output → deterministic (ECB or
   fixed-IV). Different → per-request nonce/IV.
2. **Length** — input k vs k+1 bytes. Block-step → block cipher. 1:1 →
   stream. Staircase with random size → compression first.
3. **Repetition** — 'A'*48. Repeated ciphertext blocks → ECB.
4. **Corruption** — flip a mid-ciphertext byte; check the response vs
   baseline and vs a MAC-corruption. Two answers → padding/validity oracle.
5. **Tag** — is there a separate tag field verified before decrypt? Yes →
   authenticated boundary.

## Decision table

| 1 | 2 | 3 | 4 | 5 | Route |
|---|---|---|---|---|---|
| same | block | repeat | — | no tag | ECB |
| same | block | none | 2 answers | no tag | CBC padding oracle |
| diff | 1:1 | — | — | no tag | CTR/stream |
| diff | block | none | 2 answers | tag-after | CBC + tag (weird) |
| — | — | — | uniform | tag-before | authenticated boundary |

## Signals that route elsewhere

- Predictable keystream without crypto → `../crypto-prng/`.
- Encoding/obfuscation only → `../misc-encoding-carrier/`.
- RSA shapes (modulus, exponent) → `../crypto-rsa/`.

## Output

The oracle kind + the distinguisher channel + the matched attack file.
Never a payload yet.
