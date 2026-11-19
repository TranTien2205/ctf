# Nil and missing args — the read boundary — checklist

Companion to `nil-and-missing-args.md`.

## Checklist

- [ ] 1. Scan %N$p upward — when values turn to (nil), you've passed the real
- [ ] 2. The real arg count bounds the useful N range.
- [ ] 3. Past-window reads error — treat as the scan's end.
