# Boundary cases — where the standard recipe breaks

Each entry: the boundary, why it breaks the recipe, and the fix.

## Compression before encryption

CRIME/BREACH territory: length still leaks (a guess that compresses better
makes shorter ciphertext) but byte-at-a-time fails because repeated input
compresses away. Detection: ciphertext length stops tracking input length.
Fix: the length-oracle variant — submit guesses, shorter response = better
compression = correct guess.

## Random per-request prefix

Breaks byte-at-a-time alignment but NOT cut-and-paste (a static-length
random prefix still leaves fixed block structure). Fix: measure the random
prefix length per request, or find a fixed suffix to attack backwards.

## Counter-mode block counters

CTR nonces increment per BLOCK, so two 'different nonce' messages can share
keystream on later blocks. Fix: align pairs by absolute counter value, not
message index.

## Truncated digests

sha512/256 and 128-bit-truncated SHA-256 still carry full internal state in
the published part — length extension works. A truncation below the state
width loses the tail and extension fails.

## Multi-block secrets under byte-at-a-time

Block N>1 needs a synthetic window: your input is (last 15 recovered bytes)
so the target byte lands at a boundary again — same loop, shifted offset.

## Padding-edge false positives

The \\x01-vs-longer-pad ambiguity at the last byte: two guesses both return
'valid'. Fix: always re-test with the second-to-last byte modified.

## Rate-limited oracles

A 10 req/s cap makes a 40k-request padding loop ~1 hour. Fix: measure rate
first, parallelize if the service allows, bound --max-requests.

## Padding-free modes

CTR/GCM/stream have no padding to oracle. The pad check is not the oracle —
the tag is.
