# The chain as data — writing the exploit file


The chain is bytes in a file/buffer: build it with struct.pack — the
script assembles padding + gadget addresses + args into the payload.

## The shape

    python3 -c 'import struct; p=lambda x:struct.pack("<Q",x); ...'
    # or a driver script

## The discipline

Generate the payload — don't hand-edit bytes; the script's arithmetic
is the audit.
