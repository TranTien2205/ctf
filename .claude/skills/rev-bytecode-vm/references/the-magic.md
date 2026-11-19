# The magic number — the .pyc's version lock


A .pyc's first 4 bytes are the Python version's magic — read them
BEFORE loading: the marshal format is version-locked and a
wrong-version load crashes or silently misreads.

## The read

    python3 -c "d=open('x.pyc','rb').read(); print(d[:4].hex())"
    python3 -c "import importlib.util; print(importlib.util.MAGIC_NUMBER.hex())"

Match the file's magic to your interpreter's — mismatch = wrong
interpreter or a version-matched decompiler needed.
