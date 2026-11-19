# Workflow — the ordered path — checklist

Companion to `workflow.md`.

## Checklist

- [ ] 1. Detect: a printf-family call whose format arg is your input.
- [ ] 2. Confirm: send %p.%p.%p — reflected pointers prove the primitive.
- [ ] 3. Locate: AAAA.%N$p scanning N → your buffer's argument index.
- [ ] 4. Choose: read (%p/%x/%s) or write (%n/%hn/%hhn).
- [ ] 5. If write: pick the target (GOT / ret-addr / hook) and the value.
- [ ] 6. Compose: leak (if needed) + write + redirect.
- [ ] 7. Land it; post-probe the class, pre-flag the bytes.
