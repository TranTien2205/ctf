# GOT overwrite — partial RELRO — checklist

Under partial RELRO, the GOT stays writable: overwrite an imported function's GOT slot to point at system/another function — the next call to it goes to your target.

## Checklist

- [ ] Check RELRO in pwn_triage — 'partial' means GOT is writable.
- [ ] Find an imported function called AFTER your write point with a controllable argument.
- [ ] Write the target address into that function's GOT slot.
- [ ] The next call to it goes to your target — system('/bin/sh') is the classic.

## Abort conditions

- The write must reach the GOT — stack smashes reach stack only; need arb-write or a far-enough smash.
- Partial RELRO leaves GOT writable; full RELRO binds it readonly at startup.
- A GOT overwrite needs the target's real address — a leak if ASLR.

## Falsifier

Falsifier — full RELRO: the GOT is read-only; no GOT write applies.
