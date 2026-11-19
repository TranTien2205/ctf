# The .bss write — the static target — checklist

Companion to `the-bss-write.md`.

## Checklist

- [ ] The slot array itself: write a pointer there → later ops use it.
- [ ] A count/limit global: expand the op budget.
- [ ] A state flag (is_admin): flip it — the gated path opens.
