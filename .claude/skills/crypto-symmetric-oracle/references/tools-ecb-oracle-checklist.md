# tools/ecb_oracle.py — the byte-at-a-time driver — operational checklist

The sanctioned HTTP driver for byte-at-a-time ECB: it holds request and response together, runs the guess loop, and emits the post-probe command shape hooks.py wants.

## Checklist

- [ ] Verify locally: python3 tools/ecb_oracle.py --selftest.
- [ ] Identify the injection point: which URL parameter carries plaintext — {PT} for hex, {PTB} for base64.
- [ ] Identify the response format: --resp hex if the body is a hex string, b64 for base64, raw for binary.
- [ ] Run: python3 tools/ecb_oracle.py --url 'https://target/enc?data={PTB}' --bs 16 --resp b64.
- [ ] The recovered secret bytes print incrementally; feed the flag-shaped result through pre-flag.

## Abort conditions

- {PT} vs {PTB}: hex doubles length, base64 adds padding — the service must accept whichever you pick.
- --resp raw is almost never right over HTTP — prefer hex/b64.
- --max-requests default may exceed the target's rate limit — measure first.

## Falsifier

Falsifier — no candidate byte ever matches: either not ECB, or the response format flag is wrong, or the injection point doesn't reach the encrypt call. Verify the URL template first.

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-detection.md`
