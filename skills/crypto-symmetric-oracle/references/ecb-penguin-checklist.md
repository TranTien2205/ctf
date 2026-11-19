# The ECB-penguin intuition — structure survives encryption — checklist

The famous image: a penguin bitmap encrypted under ECB still shows the
penguin. Every ECB attack is that observation formalized.

## Checklist

- [ ] CBC chains: local structure destroyed by the XOR of the previous block.
- [ ] CTR/stream: a keystream, no block mapping at all.
- [ ] GCM: same keystream property + authentication.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
