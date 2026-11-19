# Writing INTO the format buffer itself


The format string buffer is itself stack memory — %n can write into it,
but the running printf already parsed those bytes; self-writes affect
nothing until the next call.

## Notes

- Writing into the format buffer mid-call doesn't reparse — specifiers
  are consumed left-to-right.
- If the same buffer is printf'd again later, the patch applies then.
- Rarely useful; prefer direct targets.

## Falsifier

None; informational.
