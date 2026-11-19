# The verify chain — every stage's check — checklist

Companion to `heap-the-verify-chain.md`.

## Checklist

- [ ] Stage | Check
- [ ] leak | value is a plausible address
- [ ] overlap | the marker round-trips
- [ ] poison | the two-malloc walk lands
- [ ] write | the read-back confirms
- [ ] redirect | the event fires
