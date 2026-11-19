# puts leak — the raw bytes


puts writes the bytes + \n — the raw address bytes; unpack
little-endian:

    addr = struct.unpack('<Q', raw_line.ljust(8, b'\x00'))[0]
