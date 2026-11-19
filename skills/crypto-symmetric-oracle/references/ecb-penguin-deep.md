# The ECB-penguin intuition — structure survives encryption — deep

The famous image: a penguin bitmap encrypted under ECB still shows the
penguin. Every ECB attack is that observation formalized.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Structure you control | Attack |
|---|---|
| A repeated block at a chosen offset | byte-at-a-time (make the secret byte share your block) |
| A whole block's value | cut-and-paste (splice it) |
| Block boundaries themselves | reordering (move fields) |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
