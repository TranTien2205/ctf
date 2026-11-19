# RC4 biases and Salsa/ChaCha nonce reuse — deep

Stream ciphers that are NOT CTR still obey the reuse rule — the keystream
depends on (key, nonce); reuse either one and crib-drag applies.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Weakness | Shape | Use |
|---|---|---|
| Key-scheduling bias | early keystream bytes skew to the key | mostly academic in CTF |
| Invariance / single-byte bias | 'Z' byte 2 biases to 0 | statistical; needs MANY samples |
| Same key, no nonce | every message same keystream | crib-drag directly |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
