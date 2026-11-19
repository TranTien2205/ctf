# Bytecode versions — instruction sets differ

Each CPython version changes the opcode set and semantics — the dis
output is only valid for the version that unmarshalled it.

## The practical consequence

- 3.9 vs 3.10 vs 3.11/3.12: instruction names and arg semantics
  shift (3.11 introduced adaptive/specialized ops, inline caches).
- dis.dis on the RIGHT version is correct; reading 3.11 output as
  3.10 gives nonsense opnames.

## When you can't match

xdis disassembles across versions — the portable fallback when the
matching interpreter isn't installed.
