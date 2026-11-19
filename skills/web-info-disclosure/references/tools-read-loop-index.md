# tools/web/read_loop.py — proven file-read walks — index

When a read primitive already exists (a path param, an LFI), read_loop walks wordlists/profiles over it: config, secrets, flags, source profiles built in.

## Related modules

- `tools-read-loop-deep.md` — mechanism internals and boundary conditions
- `tools-read-loop-checklist.md` — the ordered operational steps
- `tools-read-loop-catalogue.md` — case enumeration

## Cross-references

`../file-read-primitives/` · `bounded-sweep.md`
