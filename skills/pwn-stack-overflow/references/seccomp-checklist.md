# Seccomp — the syscall whitelist that shapes the payload — checklist

A seccomp filter restricts which syscalls the process may make: open may be banned while openat is allowed, execve banned entirely — the shellcode or syscall-chain must use only allowed calls.

## Checklist

- [ ] Check for seccomp: `readelf -s ./chal | grep -i seccomp` or prctl in imports.
- [ ] Dump the filter if possible: r2 or a manual BPF read — which nr's are allowed.
- [ ] Build the chain from allowed calls only: openat+read+write reads the flag without execve.
- [ ] sc_gen's cat64 (open/read/write) survives a filter that bans execve.

## Abort conditions

- execve banned → no shell, but open+read+write still exfiltrates the flag.
- open banned + openat allowed → the openat(openat_v) variant.
- A filter may also ban read/write on unexpected fds — test the allowed set.

## Falsifier

Falsifier — no seccomp filter and the standard execve path exists: this file doesn't apply.
