# Smali — the dex check

apktool/baksmali disassemble classes.dex — if-eqz/if-eq branches are the deciding compares.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
