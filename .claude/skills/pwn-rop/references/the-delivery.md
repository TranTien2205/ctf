# Delivering the chain — socat and stdlib


No pwntools here — the payload travels by socat or a stdlib socket:

## socat

    (python3 -c 'import sys; sys.stdout.buffer.write(payload)'; cat) | socat - TCP:host:port

## stdlib

    import socket, struct
    s = socket.create_connection((host, port))
    s.sendall(payload + b'\n')
    resp = s.recv(4096)

## The transport traps

- \x0a inside the payload ends a line-based read.
- \x00 in an address truncates a gets-style read.
