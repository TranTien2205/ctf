# Execution context — what the payload runs as — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the service runs as a flag-reading user | the payload inherits | read flag |
| stdin/stdout are the socket | the shell connects back | rev64 or cat64 |
| a wrapper user or setuid | privileges differ | check who the flag belongs to |

## Falsifier

Falsifier — the service's context can't reach the flag file (permissions, chroot, seccomp): the flag-read fails even if code-exec succeeds.
