# The full two-stage — leak and fire


The complete dynamic exploit, assembled:

    stage1 = pad + pop_rdi + got_x + puts_plt + main
    → prints the resolved address; program loops.

    compute: libc_base = leak - sym_offset

    stage2 = pad + pop_rdi + binsh + ret + system + exit
    → the shell fires.

## The verify points

- The leak's value is pointer-range (0x7f...).
- The base is page-aligned.
- The computed addresses are plausible.
