# The call shapes — ret vs call vs jmp


- Land on a function's address via ret: the stack is its frame.
- A `call func` gadget: explicit transfer.
- A `jmp reg` gadget: the register must hold the next target.

## The return address

After landing on a function via ret, the next qword is ITS return
address — set it to continue the chain or exit.
