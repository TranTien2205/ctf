# Stack spraying — planting data for later use


Multiple inputs or env vars can plant controlled bytes at predictable
stack offsets — a string for /bin/sh, a second-stage payload, a fake
structure.

## Shapes

- An env var planted before the smash — the string's address is
  computable from the env layout.
- A first input that writes a structure the second input uses.
- argv strings as planted data.

## Falsifier

The planted data's address isn't predictable enough to reference — the
spray doesn't help.
