# Reading past the varargs — raw stack scraping — checklist

Companion to `the-arg-beyond-varargs.md`.

## Checklist

- [ ] 1. Keep raising N past the (nil) boundary — you're reading raw stack.
- [ ] 2. Return addresses appear as code pointers (0x40.../0x55...).
- [ ] 3. Saved rbp values appear as stack pointers (0x7ff...).
- [ ] 4. The canary appears at its frame position.
