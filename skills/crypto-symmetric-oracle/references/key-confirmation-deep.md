# Key confirmation and weak keys — deep

Sometimes the 'oracle' answer is 'the key worked' — a key-confirmation
protocol. Brute-forcing a small key space through it is a valid attack.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Surface | Signal | Attack |
|---|---|---|
| 'decrypt with key X' endpoint | ok/invalid | brute the key space |
| Handshake that confirms a shared key | success/fail | offline dictionary |
| Key = 4-byte PIN / 16-bit space | tiny | enumerate directly |
| Key derived from timestamp | ~seconds of space | seed-search |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
