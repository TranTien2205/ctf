# Sanitizer strips — when % is filtered — checklist

Companion to `fmtstr-sanitize-strip.md`.

## Checklist

- [ ] 1. Test: does a sent '%p' reflect as pointer or get stripped?
- [ ] 2. If stripped: find another field, or an encoding that survives.
- [ ] 3. %% produces a literal % — can't bypass a strip filter.
