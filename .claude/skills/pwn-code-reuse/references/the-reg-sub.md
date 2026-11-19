# Register substitutes — when the pop is missing


| Needed | The substitute |
|---|---|
| rdx | xor edx,edx / mov rdx,rXX / ret2csu |
| rsi | pop rsi+scratch |
| rax | xor eax,eax then add, or a fixed-value gadget |
| rdi | a mov rdi,mem gadget |

The substitute map: when the direct pop is absent, a two-instruction
sequence often suffices.
