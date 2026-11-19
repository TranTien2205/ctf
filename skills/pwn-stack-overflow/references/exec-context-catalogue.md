# Execution context — what the payload runs as — case catalogue

The exploit runs inside the process's context: its fds, its privileges, its seccomp. The flag-read or shell inherits that context.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the service runs as a flag-reading user | the payload inherits | read flag |
| 2 | stdin/stdout are the socket | the shell connects back | rev64 or cat64 |
| 3 | a wrapper user or setuid | privileges differ | check who the flag belongs to |

## Falsifier

Falsifier — the service's context can't reach the flag file (permissions, chroot, seccomp): the flag-read fails even if code-exec succeeds.
