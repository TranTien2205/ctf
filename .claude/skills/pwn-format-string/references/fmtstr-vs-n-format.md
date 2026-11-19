# When %n is disabled — the read-only fmtstr


Some builds compile printf with %n disabled (FORTIFY/_FORTIFY_SOURCE=2 +
%D_ hardening makes %n in writable memory abort). The read side survives.

## Detection

- %p works, %n aborts the process at the call.
- "*** %n in writable segment detected ***" — glibc's FORTIFY abort.

## What remains

- Full read primitive: all %p/%s leaks work.
- No %n write: the exploit must be leak-driven — leak enough to defeat
  ASLR, then a DIFFERENT primitive does the write (another bug).

## Falsifier

%n works fine: not disabled — the write route is open.
