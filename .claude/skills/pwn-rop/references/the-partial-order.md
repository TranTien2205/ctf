# The partial order — what precedes what


Hard dependencies:

- IP control before any chain entry.
- The leak before the base-dependent entries.
- A plant before its read.
- The pops before their call.
- The alignment ret before the call.

Soft: the pops' order among themselves (absent clobbers).
