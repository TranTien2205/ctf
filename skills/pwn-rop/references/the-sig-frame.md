# The sig frame — the SROP payload


The fake frame's fields (x64, offsets into it):

    +0x00-0x38: r8..r15
    +0x40: rdi    +0x48: rsi    +0x50: rbp
    +0x58: rbx    +0x60: rdx    +0x68: rax
    +0x70: rcx    +0x78: rsp    +0x80: rip
    +0x88: eflags +0x90: cs     +0x98: fs/gs
    +0xa0: ss

~248 bytes — set rip to the next gadget, the regs to its args.
