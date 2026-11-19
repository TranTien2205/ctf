# The %*c star-width — a runtime count


`*` as a width takes the value from an argument: `%*c` prints arg-value
chars. Controllable if the arg is yours; usually it's just the next arg.

## Use

- %*c%c — the star consumes an arg for the width, %c prints one.
- If the star's arg is attacker-influenced, the count is dynamic.
- Rare — most fmtstrs control only the format, not the width arg.

## Falsifier

The width arg isn't controllable: * behaves as a fixed wide count.
