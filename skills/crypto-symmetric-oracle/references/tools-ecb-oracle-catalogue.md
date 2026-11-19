# tools/ecb_oracle.py — the byte-at-a-time driver — case catalogue

The sanctioned HTTP driver for byte-at-a-time ECB: it holds request and response together, runs the guess loop, and emits the post-probe command shape hooks.py wants.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | URL template contains {PT} or {PTB} | hex or base64 plaintext injection | ready to run |
| 2 | --resp picks response encoding | hex/b64/raw decode | choose what the service emits |
| 3 | --bs is the cipher's block size | 16 for AES, 8 for DES | set before running |
| 4 | --max-requests caps the loop | rate-limit bound | match the target's budget |

## Falsifier

Falsifier — no candidate byte ever matches: either not ECB, or the response format flag is wrong, or the injection point doesn't reach the encrypt call. Verify the URL template first.

## Coverage notes

- {PT} vs {PTB}: hex doubles length, base64 adds padding — the service must accept whichever you pick.
- --resp raw is almost never right over HTTP — prefer hex/b64.
- --max-requests default may exceed the target's rate limit — measure first.

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-detection.md`
