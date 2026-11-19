# Writing near environ — stack-reach via libc — checklist

Companion to `the-environ-write.md`.

## Checklist

- [ ] 1. libc base → environ_addr = base + offset.
- [ ] 2. Read environ → a stack address (leak).
- [ ] 3. Or write environ → later env reads see your pointer's data.
