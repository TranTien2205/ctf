# The sprintf boundary — the hidden overflow + fmtstr


sprintf(dst, buf) where dst is a stack buffer is a format-string AND a
potential overflow: the specifiers' output can overflow dst.

## The compound

- sprintf writes the formatted output to dst.
- A large %Nc output overflows a stack dst.
- The format string is your input (the fmtstr), and its OUTPUT is the
  overflow.

## Steps

1. Check dst's allocation — is it a stack buffer?
2. If yes, a large %Nc output overflows it.
3. The specifiers' effect AND the output's overflow compose.

## Falsifier

dst isn't a stack buffer or the output is bounded below saved-state
distance: only the fmtstr primitive, not the overflow.
