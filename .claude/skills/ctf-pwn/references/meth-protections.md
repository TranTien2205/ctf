# Protections decide the path

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

`tools/pwn_triage.py <bin>` prints NX/PIE/canary/RELRO WITH the evidence for each - the open routes fall out of it: NX -> code-reuse, no canary -> linear smash, partial RELRO -> GOT overwrite candidates, PIE -> leak-first chains.

## Pivot

Module read -> the shared file or class skill it names.
