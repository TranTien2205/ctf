# The glibc version matrix — which targets exist — checklist

Companion to `glibc-version-matrix.md`.

## Checklist

- [ ] glibc | Hooks | GOT
- [ ] ≤ 2.34 | __malloc_hook, __free_hook writable | RELRO-dependent
- [ ] ≥ 2.35 | hooks removed | RELRO-dependent
