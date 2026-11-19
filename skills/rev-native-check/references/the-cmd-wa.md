# wa — the assembler patch


    wa jne 0x401200 @ 0x401234   # change jz to jne at the site
    wa nop @ 0x401234            # nop the branch

The patch persists to the file — verify with pdf after.
