# The ECB-penguin intuition — structure survives encryption

The famous image: a penguin bitmap encrypted under ECB still shows the
penguin. Every ECB attack is that observation formalized.

## The principle

ECB maps each 16-byte plaintext region to a ciphertext block by a fixed
function. Structure in the plaintext (repetition, alignment, fields) maps
to structure in the ciphertext. The 'attack' is always: find which
plaintext structure you control, then use it.

## Three forms

| Structure you control | Attack |
|---|---|
| A repeated block at a chosen offset | byte-at-a-time (make the secret byte share your block) |
| A whole block's value | cut-and-paste (splice it) |
| Block boundaries themselves | reordering (move fields) |

## Why nothing else works this way

- CBC chains: local structure destroyed by the XOR of the previous block.
- CTR/stream: a keystream, no block mapping at all.
- GCM: same keystream property + authentication.

## Reading a ciphertext like a bitmap

List the blocks; look for: repeats (ECB regions), constant blocks across
tokens (fixed fields or padding), blocks that change when ONE input field
changes (that field's home). The structure map IS the exploit plan.

## Falsifier

No visible block structure under any repeated input: not ECB — the
intuition is the detection.
