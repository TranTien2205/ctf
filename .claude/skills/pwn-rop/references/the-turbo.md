# Turbo modes — the shortcut endings


- A win/flag function: ret to it — the chain is one entry.
- system imported: no libc leak needed — ret2plt to it.
- one-gadget: a single ret into libc's execve point — needs the
  leak + the constraints met.

## The rule

Check the shortcuts BEFORE building the full chain — the simplest
ending the primitives allow.
