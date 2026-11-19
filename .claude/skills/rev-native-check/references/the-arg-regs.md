# The arg registers — x64


x64 SysV: rdi=arg0, rsi=arg1, rdx=arg2 — strcmp's two operands are
rdi/rsi; memcmp's third arg (n) is rdx.

## The read

    dr rdi rsi rdx          # at the call site
    ps @ rdi                # arg0 as string
    ps @ rsi                # arg1 as string
