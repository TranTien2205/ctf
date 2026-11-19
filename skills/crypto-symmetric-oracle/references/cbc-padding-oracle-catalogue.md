# CBC padding oracle — Vaudenay decryption — case catalogue

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Corrupt ciphertext yields two distinct error responses | padding oracle confirmed | drive pad_oracle loop |
| 2 | Same ciphertext replayed gives same validity answer | deterministic oracle | full decryption feasible |
| 3 | All tampering returns one generic error | no oracle — authenticated or uniform error | reclassify |

## Falsifier

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.

## Coverage notes

- Timing CAN be the distinguisher when statuses match — but you need many samples and a stable measure; prefer body/status signals.
- The false-positive at the last byte (\x01 vs a longer real pad) is the classic bug — always re-verify with a second byte change.
- Some services return 200 with an error body — --ok-regex on body text, not --ok-status.
- Rate limits kill a 40k-request attack silently; measure accepted request rate before starting and bound --max-requests.

## Cross-references

`tools-pad-oracle.md` · `response-distinguishers.md` · `cbc-bitflip.md`
