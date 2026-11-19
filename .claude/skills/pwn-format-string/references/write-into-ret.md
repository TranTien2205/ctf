# Writing the return address via %n — the details


The saved return address lives on the stack at a leakable location: a %p
dump often contains a frame pointer chain — rbp points to the previous
rbp, whose +8 is the saved return.

## The path

1. Dump %p — find a stack-pointer-shaped word (0x7ff...).
2. It's rbp of some frame — the saved return sits at rbp+8.
3. Plant rbp+8 as the %N$n argument; write the target address byte-wise.
4. On return, RIP = your value.

## Traps

- Frame-pointer omission (-fomit-frame-pointer) breaks the rbp chain —
  then the ret-addr's stack location needs a different derivation.
- Stack addresses are ASLR'd — must be leaked each run.
