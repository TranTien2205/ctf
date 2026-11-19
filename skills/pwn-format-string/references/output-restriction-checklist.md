# Output restriction — the filtered/truncated leak — checklist

Companion to `output-restriction.md`.

## Checklist

- [ ] The output is capped → truncated leak.
- [ ] A sanitizer strips %/hex → filtered.
- [ ] Only some args reachable → partial leak.
- [ ] 1. If truncated: the leak is partial — the %n write doesn't care.
- [ ] 2. If sanitized: the write still works blind.
- [ ] 3. Check which arg positions are reachable.
