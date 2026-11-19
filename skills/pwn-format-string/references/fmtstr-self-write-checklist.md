# Writing INTO the format buffer itself — checklist

Companion to `fmtstr-self-write.md`.

## Checklist

- [ ] Writing into the format buffer mid-call doesn't reparse — specifiers
- [ ] If the same buffer is printf'd again later, the patch applies then.
- [ ] Rarely useful; prefer direct targets.
