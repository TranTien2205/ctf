# Anti-patterns — moves that look right and waste budget

## Probing before naming the oracle

Sending a padding-oracle payload to an ECB endpoint: the corruption response
means nothing because the wrong oracle was assumed. Fix: run `detection.md`'s
five probes first — two minutes, saves an hour.

## Trusting a single timing measurement

One fast reject vs one slow reject proves nothing — jitter is that size.
Fix: 50+ samples each side, compare distributions not single times.

## Treating '500' as a padding oracle

A 500 from the framework (unhandled exception) is not the same channel as a
crypto layer 'bad pad'. Fix: produce BOTH corruptions (bad pad, good-pad-bad-
MAC) and require distinct answers.

## XOR'ing base64/hex

Ciphertext must be decoded before any XOR/crib-drag. XOR'ing the hex string
of two ciphertexts produces noise. Fix: unhex first, always.

## Padding-oracle loop without the false-positive check

The last byte accepts both the \\x01 guess and the real-pad guess — a loop
that takes the first valid answer decrypts garbage. Fix: re-probe with a
second byte changed.

## Six variants of the same payload

The Polynomial lesson: when the third mutation of the same idea fails, the
mechanism is wrong, not the payload. Fix: change layers, not variants — the
controller enforces this.

## Claiming a flag from a candidate

A flag-shaped string produced by the tool but not yet read from a live
response is a candidate. Only `pre-flag` on the response counts.

## Assuming the key is in the crypto

When source shows `key = os.urandom(16)` seeded by `random.seed(time())`,
the attack is PRNG-class, not oracle-class. Check seeding first.
