# Width and precision fields — controlling the count


The %Nc and %Nd specifiers print N characters: %999c outputs 999 bytes
(one arg char padded). The field width IS the count control.

| Specifier | Effect |
|---|---|
| %Nc | N bytes printed |
| %999d with width 999 | 999 chars |
| the running total | all printed bytes = the %n value |

## Steps

1. %Nc prints N chars — the count rises by N.
2. %Nd with a width of N prints N chars — same effect.
3. The %n after it writes the cumulative count.
4. Plan the count: which value do you need written?

## Falsifier

The needed value isn't reachable as a byte-count in one call: byte-wise
%hhn composition instead.
