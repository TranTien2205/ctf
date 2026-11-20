# The stdlib client skeleton

    import socket, re
    s = socket.create_connection((host, port), timeout=...)
    buf = b''
    def until(term):
        global buf
        while term not in buf:
            buf += s.recv(4096)
        out, buf = buf.split(term, 1)
        return out + term

Buffer-until-terminator is the whole framing layer.

## The whole layer

until() IS the framing — everything else is per-round logic.

## The whole layer

until() IS the framing — everything else is per-round logic.
