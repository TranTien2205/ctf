# Code-reuse evidence — the stage signals — checklist

Companion to `evidence.md`.

## Checklist

- [ ] gadget found: the r2 /R hit listing the tail.
- [ ] leak: a range-shaped value (0x55/0x7f/0x7ff).
- [ ] chain lands: r2 -d shows rip walking the gadget addresses.
- [ ] call fires: the observable behavior (a shell prompt, a file read).
- [ ] the flag: through hooks.py pre-flag.
