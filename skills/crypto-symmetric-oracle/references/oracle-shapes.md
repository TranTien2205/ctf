# Symmetric oracles: name the oracle before the attack

A symmetric oracle answers yes/no or leaks a ciphertext — the attack shape
is decided entirely by which oracle you have and which mode it's running.

## Identify the mode first

| Behavior | Mode | Attack |
|---|---|---|
| same plaintext block → same ciphertext block | ECB | byte-at-a-time, cut-and-paste |
| bit-flip in ciphertext flips the same plaintext bit | CBC (malleable) | CBC bit-flip |
| padding errors vs valid | CBC + padding | padding oracle |
| length-extension works | `MAC(secret+msg)` | hash-length extension |
| repeated key+nonce in stream | CTR/stream reuse | keystream XOR recovery |

## Byte-at-a-time (ECB oracle)

The oracle encrypts `input + secret` — feed one byte less than the block
boundary, then brute the missing byte against the dictionary:

```text
input = "A"*(blocksize - 1 - i)         # leaks secret[i] into your block
dict  = input + guess for each byte     # build 256 candidates, match the block
```

Detect ECB first: two identical plaintext blocks → identical ciphertext
blocks. `tools/crypto` has the framework; the probe is one oracle call per
guess, ~256·len queries total.

## CBC bit-flip

`P[i] = D(C[i]) ^ C[i-1]` — flip `C[i-1]` byte-for-byte to change `P[i]`
by the same delta:

```python
C[i-1] ^= known_pt ^ wanted_pt          # corrupts P[i-1], controls P[i]
```

## Padding oracle

Server answers "padding valid/invalid" on your ciphertext — walk the last
byte of `C[i-1]` until padding validates, then `P[i]` falls out:

```python
for pad in (1..blocksize):
    for g in range(256):
        C[i-1][-pad] = g                 # oracle(True) -> byte recovered
```

## Hash-length extension

`H(secret || msg || pad || extension)` — given `H(secret||msg)` and the
length of `secret`, extend the message without knowing `secret`. `hashpumpy`
or `hlextend` builds it; the gate is whether the app hashes `secret||data`
at all.

## Stream/CTR reuse

Same nonce + same key → same keystream. Two ciphertexts XOR to the plaintext
XOR — crib-drag with known words (`"the "`, `flag{`, JSON syntax) recovers
the stream.

## Falsifier

The oracle is authenticated (AEAD/GCM/poly1305), the mode is randomized per
message, or no padding/decryption answer is exposed — the cipher's own
correctness holds; the bug lives in key management or protocol misuse.

## Traps

- ECB detection needs the *same* plaintext twice — a salt or IV per message
  kills the equal-block test; look for a fixed-prefix mode instead.
- Byte-at-a-time only works when the secret is *appended* to your input —
  `secret || input` order breaks the alignment.
- The oracle's "valid padding" answer can be a timing difference, not a
  status code — measure both.
