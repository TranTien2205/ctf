# Iterate the decider, not the wrapper

Depth module for `ctf-reverse`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Each pass of obfuscation removal should end with a SMALLER unknown:
unpack once, deobfuscate once, decompile once - then re-read the
check. Budget is spent on the decider; a second pass of reading
the same obfuscated layer is the stuck signal.

## Pivot

Decider isolated -> q-check-shape for the comparison structure.
