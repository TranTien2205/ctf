# The communication — the remote protocol


A remote exploit talks a protocol: send the payload, recv the response
— the leak's bytes, the shell's banner, the flag.

## The driver

    s = socket(...)
    s.send(payload)
    leak = s.recv(...)
    # unpack, compute, send stage 2
