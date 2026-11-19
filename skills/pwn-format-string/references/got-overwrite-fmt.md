# GOT overwrite via %n — partial RELRO's prize

Under partial RELRO, the GOT is writable: plant a GOT slot's address as a %N$n arg and overwrite it — the next call to that import goes to your target.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO | GOT writable | %n to a slot |
| an import called later with controllable args | the redirect | the call |
| a GOT slot's address | the write target | plant + write |

## Steps

1. Confirm partial RELRO via pwn_triage.
2. Find an import called AFTER the write with a controllable argument.
3. Plant its GOT-slot address as a %N$n arg; write the target address.
4. The next call to the import goes to your target — system() is classic.

## Falsifier

Falsifier — full RELRO: GOT read-only; no %n-to-GOT write applies.

## Traps

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
