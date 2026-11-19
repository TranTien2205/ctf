# The magic-number table

Each CPython release has a 4-byte magic — the file's first 4 bytes vs importlib.util.MAGIC_NUMBER tells match/mismatch. A mismatch means fetch the interpreter or use xdis.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
