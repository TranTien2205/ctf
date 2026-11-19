# Ordering the ops — the write then call


A chain that both writes a string and calls: the write precedes the
call — the call's arg is the just-written address.

## The shape

    [write-gadget: plant "/bin/sh" at .bss]
    [pop rdi ; .bss_addr]
    [system]

The ordering is the dependency: the string must exist before the call
reads it.
