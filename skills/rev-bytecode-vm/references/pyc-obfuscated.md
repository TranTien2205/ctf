# Obfuscated .pyc

Dead code, weird jumps, renamed names — dis still decodes; a decompiler may fail. Read the bytecode, not the decompiled guess.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
