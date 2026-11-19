# The corruption window — how far the bug reaches


Measure the write's reach: how many bytes past the boundary, which
directions, at which offset — the window decides which metadata is
forgeable.

## The measure

- A 1-byte overflow → size LSB only (off-by-null family).
- An 8-byte write past the end → full size field.
- A bounded OOB index → a fixed slice of a struct.

## Falsifier

The window doesn't include any metadata field: the corruption is
data-only — a different class (or a different object layout) is
needed.
