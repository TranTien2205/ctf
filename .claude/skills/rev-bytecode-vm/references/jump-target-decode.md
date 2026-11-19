# Decoding jump targets — the control flow

A VM program's jumps re-route pc — decode them to follow the real
execution order, not the byte order.

## The jump forms

- jmp_rel: pc += imm — a relative hop.
- jmp_abs: pc = imm — absolute.
- jz/jnz: conditional on a flag or stack top.

## The decode

    pc = 0
    while pc < len(prog):
        op = prog[pc]
        # decode op + its immediates, follow jmp targets
        pc += opsize(op)

For a control-flow graph: follow BOTH branch targets to map every
block — a flag-checker's program is usually linear with the fail
branch exiting early.

## The block map

The program's basic blocks (jump-delimited ranges) are its structure
— the check is usually one long straight-line block.

## The dead code

Bytes never reached by a jump target are dead — decode only live
blocks.
