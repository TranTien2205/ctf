# Kernel pwn shape

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

kernel.md/kernel-techniques.md/kernel-bypass.md: modprobe/core_pattern cred overwrite, cred struct forge, stack pivoting into user mmap, SMEP/SMAP/KASLR bypass order - the userspace techniques do NOT carry over unchanged.

## Pivot

Module read -> the shared file or class skill it names.
