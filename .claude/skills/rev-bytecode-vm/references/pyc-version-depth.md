# The .pyc version problem — which marshal can read it

CPython bytecode and the marshal format are version-locked: a code
object serialized by 3.10 cannot be unmarshalled by 3.11 — marshal
either crashes or silently misreads the constant table.

## The magic identifies it

    python3 -c "d=open('x.pyc','rb').read(); print(d[:4].hex())"
    python3 -c "import importlib.util; print(importlib.util.MAGIC_NUMBER.hex())"

Match file-magic to interpreter-magic:

- Match → marshal.loads works, dis.dis works, the floor holds.
- Mismatch → either fetch that interpreter, or use a version-matched
  decompiler. Do NOT just marshal.loads — it'll fail or misread.

## When versions mismatch

Options in order of effort:

1. Fetch the matching interpreter (a container, a tarball, pyenv).
2. `xdis` — a cross-version marshal/dis library that reads many
   versions' bytecode.
3. A decompiler targeting that version (decompyle3, pycdc).

## The header before marshal

    # Python 3.7+: magic(4) + flags(4) + source-hash-or-mtime(8)
    code = marshal.loads(d[16:])
    # Older: 12-byte header
    code = marshal.loads(d[12:])

## The constant-table trap

On a wrong version, marshal may return an object whose co_consts
parses wrong — garbage strings. If the constants look like noise,
suspect the version before suspecting an obfuscator.
