# Partial pointer overwrite — low-byte aims


A write that only reaches a pointer's low byte still aims it within the
same page region — partial overwrites defeat the need for a full leak.

## Use

- Corrupting a saved fd's low byte: the bin points a few hundred bytes
  off — within heap data you can spray.
- Overwriting a function pointer's low byte: redirects within the same
  64KB region.
- On 2.32+, even a partially-known pos lets a low-byte mangled-fd edit
  aim within the page.

## Falsifier

The needed redirect is outside the partial-overwrite's reach (different
page): a full write or full leak is required.
