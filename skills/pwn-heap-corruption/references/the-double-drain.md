# Draining two bins — the mixed strategy


Some techniques need BOTH tcache and fastbin states — drain tcache for
one size, fill fastbin for another, run them together.

## The ordering

Frees interleave by size — plan the bin each free lands in; the
combined state is the setup.

## Falsifier

The op budget can't express both sequences: one bin's strategy only.
