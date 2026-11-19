# x64 vs x86 — the arg convention — checklist

Companion to `the-64-vs-32.md`.

## Checklist

- [ ] x64: args in rdi, rsi, rdx, rcx, r8, r9 — pop gadgets set them.
- [ ] x86: args on the stack — the chain embeds them after the call
