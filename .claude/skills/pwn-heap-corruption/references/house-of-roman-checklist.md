# House of roman — fastbin to __malloc_hook — checklist

Companion to `house-of-roman.md`.

## Checklist

- [ ] 1. Fastbin dup to a fake chunk overlapping __malloc_hook - 0x23.
- [ ] 2. The fake chunk's size must pass the fastbin size check — the known
- [ ] 3. Alloc returns the fake; write the one-gadget over the hook.
- [ ] 4. The next malloc fires it.
