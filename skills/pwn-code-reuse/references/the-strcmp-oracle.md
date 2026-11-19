# strcmp — the comparison oracle


strcmp(a, b) called via the chain compares memory — the crash/no-crash
or return-value difference is an oracle for byte-checking a secret.

## The recipe

    pop rdi ; guess_buf
    pop rsi ; secret_addr
    strcmp@plt
    # the result's effect branches a later gadget

Slow — n calls for n bytes — but works when no print channel exists.
