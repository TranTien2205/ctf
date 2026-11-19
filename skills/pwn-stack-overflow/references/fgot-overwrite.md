# GOT overwrite — partial RELRO

Under partial RELRO, the GOT stays writable: overwrite an imported function's GOT slot to point at system/another function — the next call to it goes to your target.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO | GOT writable | overwrite a slot |
| a function called later with a controllable arg | the call to redirect | write into its GOT |
| a write-what-where primitive | the write vector | stack smash to GOT or arb-write |

## Steps

1. Check RELRO in pwn_triage — 'partial' means GOT is writable.
2. Find an imported function called AFTER your write point with a controllable argument.
3. Write the target address into that function's GOT slot.
4. The next call to it goes to your target — system('/bin/sh') is the classic.

## Falsifier

Falsifier — full RELRO: the GOT is read-only; no GOT write applies.

## Traps

- The write must reach the GOT — stack smashes reach stack only; need arb-write or a far-enough smash.
- Partial RELRO leaves GOT writable; full RELRO binds it readonly at startup.
- A GOT overwrite needs the target's real address — a leak if ASLR.

## Commands

```bash
readelf -d ./chal | grep -i relro
readelf -r ./chal
```

## Cross-references

`ret2libc.md` · `write-where.md`
