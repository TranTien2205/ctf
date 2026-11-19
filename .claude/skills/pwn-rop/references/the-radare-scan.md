# The radare scan — the /R surface


    r2 -A ./chal
    /R pop rdi          # specific sequence
    /Rj pop             # JSON — parse in a script
    /Rl 4 pop           # limit gadget length
    /R syscall          # the kernel entry

## The audit

Every hit lists the address and the tail — verify the tail ends in
ret and the side effects are tolerable (pd 4 @ addr).
