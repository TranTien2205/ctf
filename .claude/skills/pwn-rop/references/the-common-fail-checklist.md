# The common failures — the checklist of bugs — checklist

Companion to `the-common-fail.md`.

## Checklist

- [ ] Wrong offset (re-measure).
- [ ] Bad byte in an address (pick a different gadget).
- [ ] Missing alignment ret (add one).
- [ ] Wrong libc build (re-identify).
- [ ] Unresolved GOT read (call the function first).
- [ ] Stack-arg vs register-arg confusion (the ABI).
- [ ] Chain past the read's bound (shorten or stage).
