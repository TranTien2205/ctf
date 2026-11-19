# Fmtstr-write vs stack-smash — two writes, two classes


A %n write and a stack smash are both 'write to a pointer' — the class
boundary is the MECHANISM: a format specifier vs an unbounded copy.

| Write | Class |
|---|---|
| a %n | format-string |
| a copy past a buffer | stack-smash |
| both primitives in one binary | leak + smash |

## Falsifier

The 'format string' is actually an unbounded copy: the class is
stack-overflow.
