# ret2csu — the universal call primitive — checklist

Companion to `ret2csu.md`.

## Checklist

- [ ] Set r12 = &target_func_area, rbx = 0, rbp = 1 (or loop control),
- [ ] The call fires through [r12+rbx*8] — a memory-indirect call.
