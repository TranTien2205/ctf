# GOT overwrite via %n — partial RELRO's prize — checklist

Under partial RELRO, the GOT is writable: plant a GOT slot's address as a %N$n arg and overwrite it — the next call to that import goes to your target.

## Checklist

- [ ] Confirm partial RELRO via pwn_triage.
- [ ] Find an import called AFTER the write with a controllable argument.
- [ ] Plant its GOT-slot address as a %N$n arg; write the target address.
- [ ] The next call to the import goes to your target — system() is classic.

## Abort conditions

- The GOT slot's address is known (non-PIE) or base+offset (PIE + leak).
- %n writes the whole qword — usually you want %hhn byte-wise for a controlled value.
- The target arg at the call site decides what the redirect calls.

## Falsifier

Falsifier — full RELRO: GOT read-only; no %n-to-GOT write applies.
