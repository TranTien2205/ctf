# The pop gadgets — setting the argument registers — checklist

Companion to `pop-gadgets.md`.

## Checklist

- [ ] 1. `pop rdi; ret` — the most common, needed first.
- [ ] 2. `pop rsi; ret` / `pop rdx; ret` — args 2 and 3.
- [ ] 3. `pop rax; ret` — the syscall number holder.
- [ ] 4. Combined: `pop rsi; pop r15; ret` — sets two (r15 is a scratch you
