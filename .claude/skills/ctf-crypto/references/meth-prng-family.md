# PRNG family map

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

prng*.md + prng-attacks.md: LCG from outputs (the tool exists), LFSR from keystream (Berlekamp-Massey shape), MT19937 state recovery from 624 outputs, xorshift inversion, glibc/Java/go rand quirks.

## Pivot

Module read -> the shared file or class skill it names.
