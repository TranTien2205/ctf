# Protection internals — what each mechanism actually does — checklist

Each protection is a specific mechanism with a specific failure mode — knowing the internals tells you the bypass.

## Checklist

- [ ] Canary: a random qword loaded from TLS (%fs:0x28) into each frame, XOR-checked before ret.
- [ ] NX: the stack page's PTE has the NX bit — instruction-fetch faults there.
- [ ] PIE: the executable loads at a random base; all static addresses shift.
- [ ] RELRO: partial = GOT writable after link; full = GOT read-only + all resolved at start.

## Abort conditions

- A static binary imports __stack_chk_fail even with -fno-stack-protector — the import lies.
- Partial RELRO leaves GOT writable; full RELRO makes it readonly at startup.
- ASLR is separate from PIE — a non-PIE binary has a static base even under ASLR.

## Falsifier

Falsifier — the protection doesn't behave as named (e.g., a static binary 'has' __stack_chk_fail but doesn't use it): read the evidence, not the import list.
