# Input via environment — env-var buffers — index

Environment variables land on the stack too: getenv() + strcpy into a buffer is a stack overflow via an env var.

## Related modules

- `env-control-deep.md` — boundary conditions
- `env-control-checklist.md` — operational steps
- `env-control-catalogue.md` — case enumeration

## Cross-references

`read-family.md`
