# The *-width trick — width from an argument


A '*' width takes the width from an argument: `%*c` prints arg-many
chars. If you control a width arg, you control the count — an extra
count source.

## Steps

1. `%*c` reads the width from the next arg — if that arg is yours, the
   count is yours.
2. Combines with %n: `%*c%n` writes your width-value.
3. Rare in practice — usually you control only the format.

## Falsifier

The width arg isn't controllable: %* is just a fixed-width count.
