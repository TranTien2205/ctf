# Hunting the syscall gadget — the kernel door — checklist

Companion to `the-syscall-hunt.md`.

## Checklist

- [ ] `syscall; ret` — clean.
- [ ] `syscall` inside a longer tail — audit it.
- [ ] `int 0x80` on x86 — the 32-bit form.
- [ ] `sysenter` — rare on x64.
