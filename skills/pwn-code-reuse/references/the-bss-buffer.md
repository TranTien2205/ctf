# The .bss buffer — a fixed plant region


.bss/.data have fixed addresses (non-PIE) and are writable — the
standard plant region for /bin/sh and the pivot target.

## The use

- Write "/bin/sh" into .bss via a write primitive or a read() — the
  system arg is a fixed address.
- Plant the second-stage chain there; pivot rsp into it.

## Falsifier

PIE without a base leak: even .bss moves.
