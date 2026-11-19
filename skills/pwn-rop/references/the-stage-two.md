# Stage two — the real chain


After the leak and the re-entry, the second overflow delivers the
real chain — now with computed addresses:

    pop rdi ; binsh_addr      # libc_base + str_offset
    ret                       # alignment
    system_addr               # libc_base + sys_offset

## The compute

Every stage-2 address = base + offset — the leak bought the base.
