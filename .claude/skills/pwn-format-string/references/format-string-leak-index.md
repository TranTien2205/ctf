# Format-string as a leak primitive — feeding the smash — index

A format-string read isn't always the exploit — often it's the LEAK that feeds a stack-overflow chain: the canary, the PIE base, a libc pointer.

## Related modules

- `format-string-leak-deep.md` — boundary conditions
- `format-string-leak-checklist.md` — operational steps
- `format-string-leak-catalogue.md` — case enumeration

## Cross-references

`canary-pie-composition.md` · `../pwn-stack-overflow/`
