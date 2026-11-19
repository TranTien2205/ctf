# CBC padding oracle — Vaudenay decryption — playbook

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

## Ordered playbook

1. Confirm the signal: flip a byte in the last block's preceding block; catch the pad error. Then produce VALID padding with a different error (e.g., MAC fail) — two distinguishable answers required.
2. For each byte position from the end: xor the previous block's byte so the pad becomes \x01, then \x02\x02, brute-forcing each value through 256 guesses.
3. The 'valid' response reveals the pad byte; the intermediate plaintext byte = pad XOR guess.
4. Handle the false positive at pad \x01: two candidate guesses can both validate — disambiguate by changing the second-to-last byte and re-checking.
5. tools/pad_oracle.py implements exactly this over HTTP with --ok-status/--ok-regex as the validity distinguisher.

## Falsifier

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.

## Commands

```bash
python3 tools/pad_oracle.py --ct <hex-ct-with-iv> --url 'https://target/dec?ct={CT}' --ok-regex 'OK|accepted'
python3 tools/pad_oracle.py --selftest
```
