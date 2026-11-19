# The input format — what the read accepts — checklist

Companion to `the-input-fmt.md`.

## Checklist

- [ ] gets: until newline — no 0x0a inside.
- [ ] read(n): n raw bytes — anything goes.
- [ ] scanf %s: whitespace-terminated.
- [ ] fgets: newline or n-1 — keeps the newline.
