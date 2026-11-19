# Register VM operand decoding

A register VM encodes op + register + immediate per instruction —
the byte format is per-opcode.

## The format recovery

Each handler's register/imm reads name the operand format:

    case 0x01: regs[prog[pc]] = prog[pc+1]; pc += 2;  // mov rN, imm
    case 0x02: regs[prog[pc]] ^= regs[prog[pc+1]]; pc += 2; // xor rN, rM
    case 0x10: regs[0] = input[ip++]; pc += 1;        // read

The operand width (1 or 2 bytes per reg index, imm width) varies —
read each handler to get it.

## Decoding the program

Per opcode, emit `op rA, rB, imm` — the assembly listing.
