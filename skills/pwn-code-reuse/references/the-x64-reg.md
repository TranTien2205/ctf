# The x64 registers — the arg order


Function args (x64 SysV): rdi, rsi, rdx, rcx, r8, r9 — the first six
in registers, the rest on the stack.

## The pops

Each register's pop gadget sets it; a stack-arg call for arg7+ needs
the args written onto the stack too.
