# Specifier starvation — when the fmtstr consumes the args


Too many specifiers consume args past your controlled position — the
primitive runs out of your pointers before reaching the write.

## The problem

- Each %p/%x/%s/%n consumes one argument position.
- A long run of %p before the %n walks past your planted pointer.
- Positional args %N$... don't consume — they address by index.

## Steps

1. Keep the write early, or use positional specifiers.
2. Count the consuming specifiers before your target %N.
3. Positional %N$p/%N$n address by index — no consumption.

## Falsifier

The needed write position is consumed by earlier specifiers: use
positional %N$n to address it directly.
