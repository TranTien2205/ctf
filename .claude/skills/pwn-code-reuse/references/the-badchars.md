# Bad characters in the chain — the byte filter


The input path may strip bytes (\x00, \x0a, \x0d...) — the chain's
addresses and arguments must survive the filter.

## Workarounds

- An address containing a bad byte: pick a different gadget with a
  clean address (another instance of the same instruction elsewhere).
- An argument with a bad byte: compute it (xor a value into a
  register) instead of passing it literally.
- Zero bytes in arguments: set via xor-gadgets not literals.

## Falsifier

The filter strips bytes the chain can't avoid (e.g. all addresses
contain \x0a): restructure — a staged approach where the bad bytes
arrive via a second read.
