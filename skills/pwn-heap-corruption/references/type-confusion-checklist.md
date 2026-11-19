# Type confusion via overlap — the payoff — checklist

Companion to `type-confusion.md`.

## Checklist

- [ ] 1. Overlap a data-carrying object (controllable bytes) with a
- [ ] 2. Write via the data object → the pointer object's pointer now aims
- [ ] 3. Trigger the pointer's use → read/write/call redirected.
- [ ] Small-data + function-pointer: exec redirect.
- [ ] Small-data + string-pointer: arbitrary read (print-the-pointer).
- [ ] Small-data + free-slot-pointer: free an arbitrary address (house of
