# Input transports — where the smash's bytes come from — checklist

stdin, argv, env, a socket, a file — each transport carries the payload with its own byte restrictions and re-trigger semantics.

## Checklist

- [ ] Identify the transport from the input source.
- [ ] Match the byte restrictions: argv/env can't have \x00, fgets stops at \n, a socket read is raw.
- [ ] Match the re-trigger: a looping service re-reads; a one-shot doesn't.
- [ ] Build the payload for that transport's rules.

## Abort conditions

- A socket read is raw bytes; a fgets stops at newline.
- argv/env \x00 restriction kills null bytes in addresses.
- A file-read payload can contain any byte.

## Falsifier

Falsifier — the transport isn't what you assumed (e.g., it's a socket field, not stdin): the byte-filtering/re-trigger rules change.
