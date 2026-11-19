# GOT overwrite via %n — partial RELRO's prize — deep

Under partial RELRO, the GOT is writable: plant a GOT slot's address as a %N$n arg and overwrite it — the next call to that import goes to your target.

## Mechanism internals

The format string is an interpreter: each specifier consumes an argument by position, %p/%x read, %s dereferences, %n writes the cumulative byte-count. The whole primitive is argument-position arithmetic plus count control — the exploit is locating your planted value's index N and steering the count to the value you want written.

## Boundary conditions

- x64: args 1-6 in registers; stack args N≥6.
- A literal format closes the class.
- Full RELRO closes GOT.
- glibc ≥2.35 removes the hooks.
- %s/%n reads/writes until a \x00 — null bytes truncate.
- The count is cumulative — byte-wise writes compose it.

## Falsifier

Falsifier — full RELRO: GOT read-only; no %n-to-GOT write applies.

## Highest-cost traps

- The GOT slot's address is known (non-PIE) or base+offset (PIE + leak).
- %n writes the whole qword — usually you want %hhn byte-wise for a controlled value.
- The target arg at the call site decides what the redirect calls.

## Commands

```bash
readelf -r ./chal
readelf -d ./chal | grep -i relro
```

## Cross-references

`ret-addr-overwrite.md` · `partial-write.md`
