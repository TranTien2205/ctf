# Same-page redirect — the 2-byte %hn trick — checklist

Companion to `partial-write-same-page.md`.

## Checklist

- [ ] 1. Compare the target's address with the slot's current value.
- [ ] 2. Overwrite only the differing low bytes with %hn/%hhn.
- [ ] 3. No leak needed for same-binary redirects — the high bytes stay.
