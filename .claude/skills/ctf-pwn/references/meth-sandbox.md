# Sandbox escape shape

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

seccomp-BPF filters: whitelist read -> allowed-syscall payload (open/read/write only, ORW); blacklist -> the missed syscall (openat, x32 ABI); sandbox-escape.md carries both.

## Pivot

Module read -> the shared file or class skill it names.
