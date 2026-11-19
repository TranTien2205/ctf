# Closing the class — when fmtstr is falsified


The class is closed when: (a) the input isn't the format, or (b) every
primitive route is falsified — record it and reclassify.

## Closure checks

- printf("%s", input): literal format — closed at this call.
- Every % specifier stripped by a sanitizer: closed at this input.
- %n writes reachable but every redirect slot falsified (full RELRO +
  no stack leak + new glibc + no ret): effectively closed.

## Record

    python3 tools/state.py <chal> --strategy-used reclassify

## Falsifier reversal

A literal-format call elsewhere doesn't close OTHER calls — each printf
site is its own question. Only a closed site is dead; other sites may
still be open.
