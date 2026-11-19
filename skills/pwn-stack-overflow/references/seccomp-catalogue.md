# Seccomp — the syscall whitelist that shapes the payload — case catalogue

A seccomp filter restricts which syscalls the process may make: open may be banned while openat is allowed, execve banned entirely — the shellcode or syscall-chain must use only allowed calls.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | libseccomp or prctl in imports | a filter exists | audit allowed calls |
| 2 | execve banned but open/read/write allowed | no shell, but flag-read works | cat64-style |
| 3 | open banned, openat allowed | route to openat | the alternative syscall |

## Falsifier

Falsifier — no seccomp filter and the standard execve path exists: this file doesn't apply.
