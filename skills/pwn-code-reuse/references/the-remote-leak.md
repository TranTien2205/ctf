# The remote leak — the byte protocol


On a remote service the leak arrives as bytes in a response: read the
raw bytes, unpack the address — don't expect formatted output.

## The read

    leak_bytes = recv(...)
    addr = struct.unpack('<Q', leak_bytes.ljust(8,b'\x00'))[0]
    libc_base = addr - offset

## Falsifier

The leak channel mangles bytes (text-only channel, encoding): pick a
printable-safe leak path or a different channel.
