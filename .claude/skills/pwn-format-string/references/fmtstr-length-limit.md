# Format-string length limits — fitting the payload


The input field may cap your fmtstr's length — a 64-byte field can't hold
a full pointer + many specifiers. Positional args minimize the length.

## Shrinking tricks

- %N$hhn is shorter than %N$n equivalent.
- Positional args skip the consuming specifiers.
- The pointer can ride inside the same input — one field holds both
  pointer and specifiers.

## Falsifier

The needed payload exceeds the input cap AND can't be split across
calls: route shrinks to what's expressible.
