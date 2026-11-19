# Chosen-ciphertext access — the second oracle direction

Most of this class is chosen-plaintext (you feed plaintext, watch output).
Chosen-ciphertext is the reverse: feed crafted ciphertext, watch the
decrypt behavior. The available attacks differ.

## What chosen-ciphertext gives you

| You can | Attack |
|---|---|
| Submit CT and get pad-valid answer | Vaudenay decryption |
| Submit CT and get plaintext | trivial — the flag is free |
| Submit CT and get a validity bit | format/padding oracle |
| Submit CT and get a MAC-valid bit | forgery oracle |

## Building the ciphertext

- Malleate: XOR edits into known CT (bit-flip, CTR malleability).
- Splice: reorder/copy blocks under ECB; splice IV+blocks under CBC.
- Construct: encrypt your own plaintext if an encrypt oracle also exists
  (encrypt-then-tamper-then-decrypt).

## The two-oracle combination

Chosen-plaintext + chosen-ciphertext = the strongest shape: encrypt the
probe blocks yourself, malleate them, and read the decrypt answer. Both
directions of the cipher are yours.

## Falsifier

The decrypt path is authenticated: every crafted CT rejected — the
chosen-ciphertext channel is closed.
