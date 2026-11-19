# The send loop — the interaction pattern


The driver's loop:

    s = socket.create_connection((H,P))
    s.recv(...)              # consume the prompt
    s.send(stage1 + b'\n')  # the leak chain
    leak_bytes = s.recv(...) # the print
    # compute
    s.send(stage2 + b'\n')  # the real chain
    # interact — shell commands, the flag read

## The reads

Each recv is a sync point — the protocol's rhythm.
