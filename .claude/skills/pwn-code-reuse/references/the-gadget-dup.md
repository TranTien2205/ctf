# Duplicate gadgets — many addresses, one tail


The same instruction tail exists at many addresses — pick the one with
the cleanest bytes (no bad-chars) or the shortest surrounding path.

## The choice

Several `pop rdi; ret` addresses exist — prefer one with a clean
address (no 0x0a/0x00) and minimal side effects.
