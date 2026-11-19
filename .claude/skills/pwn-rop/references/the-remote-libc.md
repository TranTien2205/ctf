# The remote libc — matching the build


The remote libc's build decides every libc offset — a mismatched
libc gives a system that calls garbage.

## The identification

1. Leak TWO resolved imports (puts + printf, say).
2. Their distance fingerprints the build.
3. Name the version; derive every offset from it.

## The sources

- The shipped libc file (exact).
- The fingerprint db (tools/gadget_lookup.py or a libc db).

## Falsifier

No match and no shipped file: offsets can't be derived — a version-
tolerant technique (ret2dlresolve, gadgets in the binary) is needed.
