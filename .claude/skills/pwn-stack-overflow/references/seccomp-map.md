# Seccomp — the syscall whitelist that shapes the payload — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| libseccomp or prctl in imports | a filter exists | audit allowed calls |
| execve banned but open/read/write allowed | no shell, but flag-read works | cat64-style |
| open banned, openat allowed | route to openat | the alternative syscall |

## Falsifier

Falsifier — no seccomp filter and the standard execve path exists: this file doesn't apply.
