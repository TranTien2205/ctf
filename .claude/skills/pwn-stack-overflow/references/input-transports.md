# Input transports — where the smash's bytes come from

stdin, argv, env, a socket, a file — each transport carries the payload with its own byte restrictions and re-trigger semantics.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| stdin read (fgets/read/scanf) | stdin transport | send + newline |
| argv[1] used directly | argv transport | arg = payload |
| getenv + copy | env transport | env var = payload |
| socket read | network transport | nc/python socket |
| fread from a file | file transport | write the file |

## Steps

1. Identify the transport from the input source.
2. Match the byte restrictions: argv/env can't have \x00, fgets stops at \n, a socket read is raw.
3. Match the re-trigger: a looping service re-reads; a one-shot doesn't.
4. Build the payload for that transport's rules.

## Falsifier

Falsifier — the transport isn't what you assumed (e.g., it's a socket field, not stdin): the byte-filtering/re-trigger rules change.

## Traps

- A socket read is raw bytes; a fgets stops at newline.
- argv/env \x00 restriction kills null bytes in addresses.
- A file-read payload can contain any byte.

## Cross-references

`read-family.md` · `bad-chars.md` · `argv-control.md`
