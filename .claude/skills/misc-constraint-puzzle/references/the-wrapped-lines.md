# Wrapped lines — a question spans lines

A long puzzle wraps mid-question — the terminator is still the
prompt mark, so buffer-until-terminator naturally rejoins the lines;
then normalize whitespace before parsing.

## Rejoin

The terminator rejoins; normalize whitespace after.
