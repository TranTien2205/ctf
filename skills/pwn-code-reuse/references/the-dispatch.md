# The dispatch — choosing by the binary's shape


| Binary shape | The route |
|---|---|
| static, has syscall | execve-by-syscall |
| dynamic, imports system | ret2libc |
| dynamic, no system | ret2dlresolve or gadget-built call |
| has a win func | ret2win |
| tiny, few gadgets | ret2csu or SROP |

The binary's shape names the route before any gadget is searched.
