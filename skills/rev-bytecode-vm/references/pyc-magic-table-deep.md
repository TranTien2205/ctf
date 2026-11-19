# The magic-number table — deep

Companion to `pyc-magic-table.md`.

Each CPython release has a 4-byte magic — the file's first 4 bytes vs importlib.util.MAGIC_NUMBER tells match/mismatch. A mismatch means fetch the interpreter or use xdis.
