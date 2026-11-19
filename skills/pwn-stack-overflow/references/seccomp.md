# Seccomp — the syscall whitelist that shapes the payload

A seccomp filter restricts which syscalls the process may make: open may be banned while openat is allowed, execve banned entirely — the shellcode or syscall-chain must use only allowed calls.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| libseccomp or prctl in imports | a filter exists | audit allowed calls |
| execve banned but open/read/write allowed | no shell, but flag-read works | cat64-style |
| open banned, openat allowed | route to openat | the alternative syscall |

## Steps

1. Check for seccomp: `readelf -s ./chal | grep -i seccomp` or prctl in imports.
2. Dump the filter if possible: r2 or a manual BPF read — which nr's are allowed.
3. Build the chain from allowed calls only: openat+read+write reads the flag without execve.
4. sc_gen's cat64 (open/read/write) survives a filter that bans execve.

## Falsifier

Falsifier — no seccomp filter and the standard execve path exists: this file doesn't apply.

## Traps

- execve banned → no shell, but open+read+write still exfiltrates the flag.
- open banned + openat allowed → the openat(openat_v) variant.
- A filter may also ban read/write on unexpected fds — test the allowed set.

## Commands

```bash
readelf -s ./chal | grep -iE 'seccomp|prctl'
```

## Cross-references

`ret2shellcode.md` · `tools-sc-gen.md`
