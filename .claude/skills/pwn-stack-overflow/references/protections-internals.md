# Protection internals — what each mechanism actually does

Each protection is a specific mechanism with a specific failure mode — knowing the internals tells you the bypass.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary: random word at frame end | checked before ret | trip on mismatch |
| NX: data pages non-executable | code can't run on stack | ROP instead |
| PIE: base randomized | addresses unknown | leak first |
| RELRO: GOT made read-only | no GOT write | full vs partial |

## Steps

1. Canary: a random qword loaded from TLS (%fs:0x28) into each frame, XOR-checked before ret.
2. NX: the stack page's PTE has the NX bit — instruction-fetch faults there.
3. PIE: the executable loads at a random base; all static addresses shift.
4. RELRO: partial = GOT writable after link; full = GOT read-only + all resolved at start.

## Falsifier

Falsifier — the protection doesn't behave as named (e.g., a static binary 'has' __stack_chk_fail but doesn't use it): read the evidence, not the import list.

## Traps

- A static binary imports __stack_chk_fail even with -fno-stack-protector — the import lies.
- Partial RELRO leaves GOT writable; full RELRO makes it readonly at startup.
- ASLR is separate from PIE — a non-PIE binary has a static base even under ASLR.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
readelf -h ./chal | grep Type
readelf -d ./chal | grep -iE 'relro|bind'
```

## Cross-references

`protection-modes.md` · `tools-pwn-triage.md`
