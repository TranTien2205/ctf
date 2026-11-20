# Question: what to overwrite

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

In priority order: saved return address, GOT entry, function-pointer field, hook family, vtable - the binary's protections decide which is writable.

## Pivot

Module read -> the shared file or class skill it names.
