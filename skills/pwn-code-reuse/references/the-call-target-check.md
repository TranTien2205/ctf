# Verifying the call target — before the chain


Before committing to a call target (system/a win func): verify it
does what you need with the args you can set.

## The check

- system: needs a string arg — the "/bin/sh" question.
- a win func: verify it actually reads the flag (disassemble it).
- a PLT import: confirm the import exists (afl / nm).

## Falsifier

The target does the wrong thing or needs args you can't supply: pick
a different ending.
