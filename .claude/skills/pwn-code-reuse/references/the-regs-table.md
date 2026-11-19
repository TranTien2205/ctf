# The register table — who holds what


| Register | Holds | Set by |
|---|---|---|
| rdi | arg0 / syscall arg0 | pop rdi |
| rsi | arg1 | pop rsi |
| rdx | arg2 | pop rdx / substitutes |
| rcx | arg3 (func) / ret-addr | pop rcx |
| r10 | syscall arg4 | rare |
| r8/r9 | args 5/6 | rare |
| rax | syscall number | pop rax |
| rsp | the stack | pivots |
| rbp | frame ptr / leave pivot | pop rbp |
