# Stack VM vs register VM — the decode differs

## Stack VM

Operands on a stack: `push 1; push 2; add; push 3; cmp` — pops feed
ops. The program is a postfix sequence.

## Register VM

Operands in registers: `mov r0, input[i]; xor r0, 0x37; cmp r0,
exp` — the byte stream encodes op+reg+imm.

## The decode

Recover the operand format per opcode — how many immediate bytes,
which registers — before reading the program.
