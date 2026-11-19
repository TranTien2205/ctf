# Tcache poisoning — aiming the fd pointer — checklist

Companion to `tcache-poisoning.md`.

## Checklist

- [ ] 1. Free a chunk → it lands in tcache with a real fd.
- [ ] 2. UAF-write or overflow: set fd = target_address.
- [ ] 3. Two mallocs of that size: first returns the freed chunk, second
- [ ] 4. Write into the "allocated" chunk → arbitrary write.
