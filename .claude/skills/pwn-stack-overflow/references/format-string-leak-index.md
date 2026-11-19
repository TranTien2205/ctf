# Format string as a leak primitive — index

A format-string read (%p, %s, %x) dumps stack/registers — the leak primitive that feeds canary and PLE leaks. Ownership is pwn-format-string's class; this file is the bridge.

## Related modules

- `format-string-leak-deep.md` — boundary conditions
- `format-string-leak-checklist.md` — operational steps
- `format-string-leak-catalogue.md` — case enumeration

## Cross-references

`../pwn-format-string/` · `canary-bypass.md` · `pie-leak.md`
