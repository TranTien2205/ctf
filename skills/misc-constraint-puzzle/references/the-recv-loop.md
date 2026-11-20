# The recv loop — the framing primitive

    def until(term):
        global buf
        while term not in buf:
            chunk = s.recv(4096)
            if not chunk: raise EOFError(buf)
            buf += chunk
        out, buf = buf.split(term, 1)
        return out + term

Empty recv = server closed; raise with the partial buffer for the log.

## EOF

b'' = closed — raise with the partial buffer for the log.

## EOF

b'' = closed — raise with the partial buffer for the log.
