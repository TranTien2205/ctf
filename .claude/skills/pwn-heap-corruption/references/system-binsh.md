# system + /bin/sh — the boring reliable end


The reliable ending: a hook/vtable/app-pointer write lands `system`,
and the fired call's argument is "/bin/sh".

## Requirements

- libc leak → system's address.
- A writable call-slot the process will invoke with a string arg.
- The string: write "/bin/sh" into a freed chunk (whose address is the
  arg — __free_hook), or aim at a call site whose arg register you
  control.

## Steps

1. __free_hook = system; free(chunk starting "/bin/sh").
2. Or: FILE vtable write landing system on a flush call.

## Falsifier

No call site passes a controllable string: the shell path needs a
different shape (one-gadget, execve chain).
