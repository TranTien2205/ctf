# Partial order — what must precede what


Hard dependencies in the chain:

- The leak before the base computation.
- The plant before the read of it.
- The pops before the call.
- The write before its firing event.

Soft: the pops' order among themselves.
