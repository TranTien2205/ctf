# Block alignment — prefix, suffix, boundary math — case catalogue

Every ECB/ECB-CBC trick lives or dies on alignment: where the service's fixed prefix ends and your controllable block boundary begins. Measure it before building any guess block.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Duplicate blocks appear at a non-block offset | fixed prefix shifts alignment | pad to the next boundary |
| 2 | Same input, different ciphertext each request | random prefix or random IV | reclassify — ECB assumption breaks |
| 3 | Your input boundary never aligns to the cipher block | streaming mode or compression | compression-aware variant |

## Falsifier

Falsifier — no input length ever produces two adjacent identical blocks: there is no ECB region reachable, the mode is not ECB, or compression precedes encryption.

## Coverage notes

- Padding under PKCS#7 adds a full block when input ≡ 0 (mod block) — alignment math must include the pad block.
- URL-safe base64 of the ciphertext shifts byte positions by 4/3 — always measure on decoded bytes.
- A prefix that changes per-request but is constant within a request still lets cut-and-paste work once the length is measured per-request.

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md`
