# Execution context — what the payload runs as — index

The exploit runs inside the process's context: its fds, its privileges, its seccomp. The flag-read or shell inherits that context.

## Related modules

- `exec-context-deep.md` — boundary conditions
- `exec-context-checklist.md` — operational steps
- `exec-context-catalogue.md` — case enumeration

## Cross-references

`tools-sc-gen.md` · `seccomp.md`
