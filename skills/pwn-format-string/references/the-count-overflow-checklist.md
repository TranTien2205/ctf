# The count overflow — the count wraps — checklist

Companion to `the-count-overflow.md`.

## Checklist

- [ ] %hhn writes count&0xff — only the low byte lands.
- [ ] Set the count so its low byte is your target byte.
- [ ] A count of 0x141 writes 0x41 via %hhn.
- [ ] 1. Plan each %hhn's running count for its target byte.
- [ ] 2. The count mod 256 is what %hhn writes.
- [ ] 3. The high bits of the count are free — pad with %% or %c.
