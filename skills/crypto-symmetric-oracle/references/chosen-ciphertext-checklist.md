# Chosen-ciphertext access — the second oracle direction — checklist

Most of this class is chosen-plaintext (you feed plaintext, watch output).
Chosen-ciphertext is the reverse: feed crafted ciphertext, watch the
decrypt behavior. The available attacks differ.

## Checklist

- [ ] Malleate: XOR edits into known CT (bit-flip, CTR malleability).
- [ ] Splice: reorder/copy blocks under ECB; splice IV+blocks under CBC.
- [ ] Construct: encrypt your own plaintext if an encrypt oracle also exists

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
