# CBC IV prediction — the BEAST-shaped case

When the IV for the NEXT message is predictable (chained from the previous
ciphertext block — the old TLS1.0 bug), chosen plaintext verifies guesses.

## Mechanism

- IV_next = C_last of the previous message.
- To test whether a captured block decrypts to guess G: submit plaintext
  G XOR IV_prev-captured XOR IV_next-predicted. If the produced block equals
  the captured ciphertext, the guess was right.

## Preconditions

| Need | Check |
|---|---|
| You see IV_next before choosing plaintext | the protocol emits it |
| You can submit chosen plaintext blocks | an encrypt oracle |
| Byte-boundary control | prefix alignment as in ECB |

## Detection

- Source shows `iv = last_ct_block` or a counter/timestamp IV.
- Capture two consecutive encrypted messages: IV2 == C1_last of message 1?

## The loop

For each byte of the secret region, align so it lands at a block start, run
the guess-verification per byte — the same rhythm as byte-at-a-time but the
answer is 'block matches' not 'pad ok'.

## Falsifier

IV is random per message and never emitted early: no prediction exists —
the attack closes.
