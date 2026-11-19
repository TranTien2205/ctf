# Code-reuse evidence — the stage signals


## Signals per stage

- gadget found: the r2 /R hit listing the tail.
- leak: a range-shaped value (0x55/0x7f/0x7ff).
- chain lands: r2 -d shows rip walking the gadget addresses.
- call fires: the observable behavior (a shell prompt, a file read).
- the flag: through hooks.py pre-flag.

## The proof standard

A flag counts only via the hook:

    python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source response --evidence '<excerpt>'

A clean exit after a chain is NOT a signal — the target action must be
observed.
