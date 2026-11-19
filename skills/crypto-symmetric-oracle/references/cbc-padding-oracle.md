# CBC padding oracle — Vaudenay decryption

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Corrupt ciphertext yields two distinct error responses | padding oracle confirmed | drive pad_oracle loop |
| Same ciphertext replayed gives same validity answer | deterministic oracle | full decryption feasible |
| All tampering returns one generic error | no oracle — authenticated or uniform error | reclassify |

## Steps

1. Confirm the signal: flip a byte in the last block's preceding block; catch the pad error. Then produce VALID padding with a different error (e.g., MAC fail) — two distinguishable answers required.
2. For each byte position from the end: xor the previous block's byte so the pad becomes \x01, then \x02\x02, brute-forcing each value through 256 guesses.
3. The 'valid' response reveals the pad byte; the intermediate plaintext byte = pad XOR guess.
4. Handle the false positive at pad \x01: two candidate guesses can both validate — disambiguate by changing the second-to-last byte and re-checking.
5. tools/pad_oracle.py implements exactly this over HTTP with --ok-status/--ok-regex as the validity distinguisher.

## Falsifier

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.

## Traps

- Timing CAN be the distinguisher when statuses match — but you need many samples and a stable measure; prefer body/status signals.
- The false-positive at the last byte (\x01 vs a longer real pad) is the classic bug — always re-verify with a second byte change.
- Some services return 200 with an error body — --ok-regex on body text, not --ok-status.
- Rate limits kill a 40k-request attack silently; measure accepted request rate before starting and bound --max-requests.

## Commands

```bash
python3 tools/pad_oracle.py --ct <hex-ct-with-iv> --url 'https://target/dec?ct={CT}' --ok-regex 'OK|accepted'
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`tools-pad-oracle.md` · `response-distinguishers.md` · `cbc-bitflip.md`
