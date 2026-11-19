# Register substitutes — when the pop is missing — map

Companion to `the-reg-sub.md`.

| Needed | The substitute |
|---|---|
| rdx | xor edx,edx / mov rdx,rXX / ret2csu |
| rsi | pop rsi+scratch |
| rax | xor eax,eax then add, or a fixed-value gadget |
| rdi | a mov rdi,mem gadget |
