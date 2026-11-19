# argv NULL — execve's second arg


execve's argv arg: NULL (rsi=0) is accepted — the simplest chain
sets rsi=0 via a pop or xor.

## The alternative

A real argv: [path_ptr, 0] in memory — the two-qword array planted.
