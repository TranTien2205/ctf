# Checking the ABI — before the chain


    file ./chal        # ELF 64-bit / 32-bit
    the class decides: pops+regs (x64) vs stack args (x86).

## The wrong-ABI bug

A SysV chain on an x86 binary: the pops set registers nobody reads —
silent failure.
