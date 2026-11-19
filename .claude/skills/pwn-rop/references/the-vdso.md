# The vDSO — kernel calls without syscalls


The virtual dynamic shared object — kernel-exported functions
(gettimeofday, clock_gettime) callable like library functions —
mapped at an ASLR'd address (AT_SYSINFO_EHDR).

## The use

A call surface that needs no syscall instruction — an exotic
primitive for filtered environments.
