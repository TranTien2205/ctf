# Register args as leak sources — rsi..r9 values — checklist

Companion to `fmtstr-the-regs-arg.md`.

## Checklist

- [ ] 1. The register args hold whatever the caller passed — often useful
- [ ] 2. rsi may be a buffer pointer; rdx a length.
- [ ] 3. These are the call's actual varargs — not stack memory.
