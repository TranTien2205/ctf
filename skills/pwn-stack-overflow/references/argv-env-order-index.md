# The argv/env layout — predicting stack contents — index

argv and env sit at the top of the stack: the first bytes a main() frame sees. Their layout predicts what the uninitialized-read leaks and where your shellcode/string can live.

## Related modules

- `argv-env-order-deep.md` — boundary conditions
- `argv-env-order-checklist.md` — operational steps
- `argv-env-order-catalogue.md` — case enumeration

## Cross-references

`env-control.md` · `argv-control.md`
