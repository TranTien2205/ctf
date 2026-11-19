# The banner read — consuming the prompt


Remote services send a prompt before reading — the script must
consume it:

    s.recvuntil(b'> ')      # or a fixed-size recv

## The trap

An unconsumed prompt shifts the recv boundary — the leak's bytes get
mixed with prompt text; consume exactly.
