# Input via argv — when the read is the command line — index

Some binaries take input as argv[1] instead of stdin: the overflow is in an argument. The payload goes in the argument position.

## Related modules

- `argv-control-deep.md` — boundary conditions
- `argv-control-checklist.md` — operational steps
- `argv-control-catalogue.md` — case enumeration

## Cross-references

`read-family.md`
