# SROP — sigreturn-oriented programming — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| syscall;ret gadget exists | srop possible | one gadget + the frame |
| you control 300+ bytes of stack | frame fits | lay out the rt_sigframe |
| need control of many registers at once | srop is the answer | one syscall |

## Falsifier

Falsifier — no syscall;ret gadget, or the stack can't hold the frame: SROP is out.
