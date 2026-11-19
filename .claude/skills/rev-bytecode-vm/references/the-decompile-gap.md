# The decompile gap — when to stop decompiling

Decompilers (uncompyle6, decompyle3, pycdc) turn bytecode into
Python — convenient when they work, but:

## The gaps

- uncompyle6/decompyle3: up to ~3.8 only.
- 3.9+: incomplete; modern adaptive bytecode defeats them.
- Obfuscated bytecode (dead code, weird jumps): decompilers fail.

## The rule

dis is the floor — ALWAYS start with dis, and fall back to it when
a decompiler produces garbage. The check's logic is legible in
bytecode even when it's not legible in decompiled source.
