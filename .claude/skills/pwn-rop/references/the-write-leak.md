# write leak — the counted bytes


write(1, addr, 8) emits exactly 8 raw bytes — recv exactly 8:

    addr = struct.unpack('<Q', s.recv(8))[0]
