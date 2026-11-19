# Calling the PLT — the imported functions


Every imported function has a PLT stub — a known call target needing
no libc leak for the CALL (the PLT is in the binary, PIE-relative).

## The trick

call puts@plt with rdi = a GOT entry — the leak; or call read@plt to
pull stage 2 — the PLT is addressable without a libc leak (only the
libc targets need it).

## Falsifier

PIE without a code leak: even the PLT's address is unknown.
