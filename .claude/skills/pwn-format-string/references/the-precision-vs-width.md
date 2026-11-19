# Precision vs width — the two count controls


The field WIDTH (%999c) and the PRECISION (%999d) both pad the printed
count — the two ways to steer %n's value.

| Specifier | Effect |
|---|---|
| %999c | width = 999 bytes |
| %999d | precision/width = 999 |
| %.999s | precision caps output |

## Steps

1. %Nc prints N chars — the count rises by N.
2. %Nd with a field width of N prints N chars — same effect.
3. %.Ns PRECISION caps a string's printed length — a limit.

## Falsifier

Neither field reaches the needed count: byte-wise %hhn composition.
