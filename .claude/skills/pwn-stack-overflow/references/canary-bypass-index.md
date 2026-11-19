# Stack canary — leak it or write around it — index

A stack canary is a random word placed before the saved frame; smashing past it trips __stack_chk_fail. The bypass is always the same shape: get the canary's value, keep it intact in your payload.

## Related modules

- `canary-bypass-deep.md` — boundary conditions
- `canary-bypass-checklist.md` — operational steps
- `canary-bypass-catalogue.md` — case enumeration

## Cross-references

`protection-modes.md` · `format-string-leak.md` · `pie-leak.md`
