# Execution context — what the payload runs as — checklist

The exploit runs inside the process's context: its fds, its privileges, its seccomp. The flag-read or shell inherits that context.

## Checklist

- [ ] The payload executes as the service's user — check who owns the flag file.
- [ ] stdin/stdout on a socket service are the socket — a shell or cat64 talks over the connection.
- [ ] seccomp or a chroot may bound what the payload can reach.
- [ ] The flag path may be /flag, ./flag, flag.txt — find it from the service's setup.

## Abort conditions

- cat64's --path must match where the flag actually is.
- A socket service's fd 0/1 is the socket — rev64 connects OUT, cat64 writes to the socket.
- A setuid binary vs a network service have different exec-contexts.

## Falsifier

Falsifier — the service's context can't reach the flag file (permissions, chroot, seccomp): the flag-read fails even if code-exec succeeds.
