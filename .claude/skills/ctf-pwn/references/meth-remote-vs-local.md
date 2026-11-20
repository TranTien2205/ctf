# Local vs remote differences

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

argv/env layout shifts between direct exec and the service wrapper - offsets that land locally can shift remotely; test the payload against the REMOTE shape (socat wrapper, docker) not only the file.

## Pivot

Module read -> the shared file or class skill it names.
