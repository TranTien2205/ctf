# Where the flag lives — targeting the final read


A heap exploit ends at a flag source: a flag file (shell/exec), a flag
in memory (read it), or a flag behind a gate (the write flips the gate).

## Endings

- system("/bin/sh") via hook/vtable → cat flag.
- Arbitrary read of a flag buffer → the flag bytes themselves.
- A write that sets the "authorized" flag → the gated path prints it.

## The choice

The write you can reach decides the ending: arbitrary-read-only → read
the flag; full write + call → exec the reader.
