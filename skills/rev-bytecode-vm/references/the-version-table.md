# The version table — magic per release


Each Python version's magic differs — the first 2 bytes' little-
endian number maps to a release. If the .pyc is for another version:
either fetch that interpreter or a version-matched decompiler.
