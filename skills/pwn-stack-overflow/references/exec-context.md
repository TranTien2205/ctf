# Execution context — what the payload runs as

The exploit runs inside the process's context: its fds, its privileges, its seccomp. The flag-read or shell inherits that context.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the service runs as a flag-reading user | the payload inherits | read flag |
| stdin/stdout are the socket | the shell connects back | rev64 or cat64 |
| a wrapper user or setuid | privileges differ | check who the flag belongs to |

## Steps

1. The payload executes as the service's user — check who owns the flag file.
2. stdin/stdout on a socket service are the socket — a shell or cat64 talks over the connection.
3. seccomp or a chroot may bound what the payload can reach.
4. The flag path may be /flag, ./flag, flag.txt — find it from the service's setup.

## Falsifier

Falsifier — the service's context can't reach the flag file (permissions, chroot, seccomp): the flag-read fails even if code-exec succeeds.

## Traps

- cat64's --path must match where the flag actually is.
- A socket service's fd 0/1 is the socket — rev64 connects OUT, cat64 writes to the socket.
- A setuid binary vs a network service have different exec-contexts.

## Commands

```bash
python3 tools/sc_gen.py cat64 --path /flag --raw
```

## Cross-references

`tools-sc-gen.md` · `seccomp.md`
