# The x86 chain — the 4-byte world


x86 specifics: p32 not p64; args on the stack; int 0x80 not syscall;
the PLT/GOT roles the same; the gadget shapes the same idea.

## The pack

    p = lambda x: struct.pack('<I', x)
