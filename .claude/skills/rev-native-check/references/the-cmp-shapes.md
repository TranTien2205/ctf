# The cmp shapes — the instruction forms


- cmp rax, imm — a constant compare.
- cmp rax, [rbx] — vs a memory value.
- test rax, rax + jz — a zero/nonzero check.
- call strcmp/memcmp then test eax — the function-compare form.

## The decide

The branch instruction after the compare is the decision point — jz
falls through or jumps to a side.
