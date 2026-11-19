# rbp vs rsp — the two stack registers — checklist

Companion to `the-fp-vs-sp.md`.

## Checklist

- [ ] rsp: the chain's walk pointer — ret reads [rsp].
- [ ] rbp: the frame pointer — only the leave;ret pivot uses it.
