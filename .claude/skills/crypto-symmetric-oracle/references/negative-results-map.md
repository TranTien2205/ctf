# Negative results — what to record when the answer is no — map

| Tested | Negative observation | Reopens if |
|---|---|---|
| ECB | no duplicate block in 'A'*48 | a different injection point exists |
| Padding oracle | identical reject for every corruption | a second endpoint decrypts |
| Nonce reuse | all captured nonces distinct | more captures become available |
| Length extension | forge rejected at secret-len 8..64 | construction shown to be raw-hash |
| Bit-flip | parser rejects all garbage blocks | a don't-care field is found |
| Timing oracle | distributions overlap at 200 samples | the service gets quieter |
| Key path | no key/seed material in handout | new source surfaces |

Expanded rows and abort conditions: `negative-results.md` and `negative-results-deep.md`.
