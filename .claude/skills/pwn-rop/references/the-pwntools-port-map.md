# Porting pwntools templates — to stdlib — map

Companion to `the-pwntools-port.md`.

| pwntools | stdlib |
|---|---|
| p64(x) | struct.pack('<Q', x) |
| u64(b) | struct.unpack('<Q', b.ljust(8,b'\x00'))[0] |
| ELF('.').got['x'] | readelf -r / r2's relocations |
| ELF('.').plt['x'] | the stub from r2's disasm |
| ELF('.').sym['x'] | nm / r2's afl |
| ELF('.').search(b'x') | strings -t x |
| process() | socket or subprocess |
| p.sendline | s.send(payload + b'\n') |
| p.recvline | s.recv / buffered read |
| ROP(elf) | tools/rop_chain.py |
