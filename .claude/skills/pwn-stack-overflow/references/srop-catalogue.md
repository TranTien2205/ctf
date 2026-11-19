# SROP — sigreturn-oriented programming — case catalogue

A sigreturn syscall (nr 15 on x64, nr 139 on x86) restores the whole CPU state from a crafted frame on the stack — total register control with one gadget.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | syscall;ret gadget exists | srop possible | one gadget + the frame |
| 2 | you control 300+ bytes of stack | frame fits | lay out the rt_sigframe |
| 3 | need control of many registers at once | srop is the answer | one syscall |

## Falsifier

Falsifier — no syscall;ret gadget, or the stack can't hold the frame: SROP is out.
