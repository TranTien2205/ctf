# The leak's shape — the bytes that come back


A leak returns raw bytes — the address is the first 6-8 (x64) or 4
(x86) little-endian bytes; unpack them.

## The unpack

    addr = struct.unpack('<Q', raw.ljust(8, b'\x00'))[0]
    base = addr - KNOWN_OFFSET

## The verify

The value must be a plausible pointer (0x55/0x56, 0x7f, 0x7ff range)
— a small int means you read the wrong field.
