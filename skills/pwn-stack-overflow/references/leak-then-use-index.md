# Leak-then-use — composing the two primitives — index

The standard hard-case chain: an info-leak primitive (format-string, uninit read) feeds values into the stack-smash payload — leak first, exploit second.

## Related modules

- `leak-then-use-deep.md` — boundary conditions
- `leak-then-use-checklist.md` — operational steps
- `leak-then-use-catalogue.md` — case enumeration

## Cross-references

`second-stage.md` · `one-shot-constraints.md`
