# Verifying the leak — the sanity checks


Before computing from a leak:

- Range: 0x55..../0x56.... (PIE binary) or 0x7f.... (libc/stack).
- Alignment: a mapped address's low 12 bits vary; a base is
  page-aligned (low 12 bits zero AFTER subtracting the symbol's
  offset).
- Distance: two leaks from the same region should be a known delta
  apart.

## Falsifier

A small integer or a string-looking value: you read the wrong field.
