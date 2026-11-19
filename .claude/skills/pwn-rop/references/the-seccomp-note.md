# The seccomp note — the filtered syscall


A seccomp filter may allow only some syscalls — execve blocked, ORW
allowed: the open/read/write chain is the answer.

## The check

prctl/seccomp presence in imports; the filter's allowed set decides
which syscalls the chain may use.
