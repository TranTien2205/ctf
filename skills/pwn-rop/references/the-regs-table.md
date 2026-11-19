# The registers table — the cheat sheet


| Reg | Role | Set by |
|---|---|---|
| rax | syscall num / return | pop rax |
| rdi | arg0 | pop rdi |
| rsi | arg1 | pop rsi |
| rdx | arg2 | pop rdx |
| rcx | arg3 (funcs) | pop rcx |
| r10 | syscall arg4 | rare |
| r8/r9 | args 5/6 | rare |
| rbp | frame ptr / pivot | pop rbp / saved-rbp |
| rsp | the chain's IP | pivots |
| rbx,r12-r15 | callee-saved / csu | the csu pops |
