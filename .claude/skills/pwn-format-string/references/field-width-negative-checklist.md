# The *-width trick — width from an argument — checklist

Companion to `field-width-negative.md`.

## Checklist

- [ ] 1. `%*c` reads the width from the next arg — if that arg is yours, the
- [ ] 2. Combines with %n: `%*c%n` writes your width-value.
- [ ] 3. Rare in practice — usually you control only the format.
