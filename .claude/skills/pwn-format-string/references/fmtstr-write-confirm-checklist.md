# Confirming the write — read-back verification — checklist

Companion to `fmtstr-write-confirm.md`.

## Checklist

- [ ] 1. Write: <ptr>.%Nc.%M$hhn plants the byte.
- [ ] 2. Read-back: %N$s on the slot prints its (changed) contents.
- [ ] 3. Compare to the intended value.
- [ ] 4. Only then fire the redirect (call the import / return / free).
