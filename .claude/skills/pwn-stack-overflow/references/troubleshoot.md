# Troubleshooting — symptom → cause → fix

| Symptom | Likely cause | Fix |
|---|---|---|
| crash but RIP isn't pattern bytes | write didn't reach saved state | re-check bound, try longer pattern |
| cyclic --find returns -1 | the 4 bytes aren't in the pattern | the fault isn't RIP — read the right register |
| works locally, crashes remotely | stack alignment (movaps) | add a 'ret' gadget for parity |
| system@plt crashes inside libc | arg/alignment | check rdi and stack parity |
| ROP chain runs but execve fails | wrong arg registers | x64: rdi/rsi/rdx; x86: stack |
| canary check fires before return | corrupted canary | leak and preserve it |
| exploit works then crashes | shellcode has banned bytes | sc_gen reports them — pick a clean stub |
| offset differs per run | ASLR/fork layout | the offset is deterministic; the ADDRESSES aren't — only offset is stable |
| one-shot service, need two stages | can't re-trigger | compose leak+smash in one input |
| PIE, everything's unknown | no base | leak or partial-overwrite first |
| 'ret' before call crashes | alignment was fine | remove the ret — parity the other way |
| payload gets truncated | a banned byte | find which byte the read strips |
