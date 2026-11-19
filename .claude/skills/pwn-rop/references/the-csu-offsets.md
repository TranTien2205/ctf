# The csu offsets — finding the gadgets


__libc_csu_init's tail: the last ~40 bytes — gadget1 (the six-pop)
sits at the function's end - 64; gadget2 (the mov/call block) about
24 bytes earlier — find them by disassembling the function's tail:

    r2 -A ./chal ; pdf @ sym.__libc_csu_init | tail -40
