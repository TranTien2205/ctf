# Hunting the syscall gadget — the kernel door


    /R syscall

## The forms

- `syscall; ret` — clean.
- `syscall` inside a longer tail — audit it.
- `int 0x80` on x86 — the 32-bit form.
- `sysenter` — rare on x64.

## Falsifier

Absent in a static binary AND no dynamic path: no direct kernel
entry — the libc call route is the alternative.
