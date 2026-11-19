# The recv boundary — delimiting the leak


The leak's bytes: up to the next newline or a fixed count — the
unpack reads the first 8 bytes of the address region.

## The robust way

    raw = s.recv(4096)
    leak_line = raw.split(b'\n')[0]     # the line the print wrote
    addr = struct.unpack('<Q', leak_line.ljust(8,b'\x00'))[0]
