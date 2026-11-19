# Chosen-ciphertext access — the second oracle direction — deep

Most of this class is chosen-plaintext (you feed plaintext, watch output).
Chosen-ciphertext is the reverse: feed crafted ciphertext, watch the
decrypt behavior. The available attacks differ.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| You can | Attack |
|---|---|
| Submit CT and get pad-valid answer | Vaudenay decryption |
| Submit CT and get plaintext | trivial — the flag is free |
| Submit CT and get a validity bit | format/padding oracle |
| Submit CT and get a MAC-valid bit | forgery oracle |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
