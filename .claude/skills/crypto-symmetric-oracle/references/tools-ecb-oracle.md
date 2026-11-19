# tools/ecb_oracle.py — the byte-at-a-time driver

The sanctioned HTTP driver for byte-at-a-time ECB: it holds request and response together, runs the guess loop, and emits the post-probe command shape hooks.py wants.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| URL template contains {PT} or {PTB} | hex or base64 plaintext injection | ready to run |
| --resp picks response encoding | hex/b64/raw decode | choose what the service emits |
| --bs is the cipher's block size | 16 for AES, 8 for DES | set before running |
| --max-requests caps the loop | rate-limit bound | match the target's budget |

## Steps

1. Verify locally: python3 tools/ecb_oracle.py --selftest.
2. Identify the injection point: which URL parameter carries plaintext — {PT} for hex, {PTB} for base64.
3. Identify the response format: --resp hex if the body is a hex string, b64 for base64, raw for binary.
4. Run: python3 tools/ecb_oracle.py --url 'https://target/enc?data={PTB}' --bs 16 --resp b64.
5. The recovered secret bytes print incrementally; feed the flag-shaped result through pre-flag.

## Falsifier

Falsifier — no candidate byte ever matches: either not ECB, or the response format flag is wrong, or the injection point doesn't reach the encrypt call. Verify the URL template first.

## Traps

- {PT} vs {PTB}: hex doubles length, base64 adds padding — the service must accept whichever you pick.
- --resp raw is almost never right over HTTP — prefer hex/b64.
- --max-requests default may exceed the target's rate limit — measure first.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
python3 tools/ecb_oracle.py --url 'https://t/e?d={PTB}' --bs 16 --resp b64
```

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-detection.md`
