# Block alignment — prefix, suffix, boundary math — operational checklist

Every ECB/ECB-CBC trick lives or dies on alignment: where the service's fixed prefix ends and your controllable block boundary begins. Measure it before building any guess block.

## Checklist

- [ ] Submit 'A'*k for k = 0..2*block; find the SMALLEST k where two identical adjacent blocks appear — the fixed prefix length is then derived.
- [ ] prefix_len = index_of_first_duplicate - (k - block). Verify by adding prefix_len_padding and seeing the duplicate move to a boundary.
- [ ] For byte-at-a-time: the attack block starts at ceil(prefix_len/block)*block; your pad fills the gap.
- [ ] When a random prefix exists, try to find any fixed suffix (a trailer the service appends) — exploit that instead.

## Abort conditions

- Padding under PKCS#7 adds a full block when input ≡ 0 (mod block) — alignment math must include the pad block.
- URL-safe base64 of the ciphertext shifts byte positions by 4/3 — always measure on decoded bytes.
- A prefix that changes per-request but is constant within a request still lets cut-and-paste work once the length is measured per-request.

## Falsifier

Falsifier — no input length ever produces two adjacent identical blocks: there is no ECB region reachable, the mode is not ECB, or compression precedes encryption.

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md`
