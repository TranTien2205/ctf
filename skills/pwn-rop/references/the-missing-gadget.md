# The missing gadget — the substitutes


| Needed | Substitute |
|---|---|
| pop rdx | xor edx,edx + a mov, or ret2csu |
| pop rsi | pop rsi+scratch two-pop |
| pop rax | a fixed-value write, or inc/dec paths |
| syscall | ret2libc instead — a libc call needs no syscall gadget |
| any call primitive | ret2csu's universal call |

## The falsifier

No substitute exists — the route is closed; pick a different ending.
