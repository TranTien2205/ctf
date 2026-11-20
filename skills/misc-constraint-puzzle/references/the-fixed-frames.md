# Fixed-length frames — recv_exact

When the protocol has no terminator, frames come at fixed sizes:

    def recv_exact(n):
        out = b''
        while len(out) < n:
            chunk = s.recv(n - len(out))
            if not chunk: raise EOFError
            out += chunk
        return out

## recv_exact

Loop until n bytes — no terminator exists.
