# The write chain — the full recipe


The complete arbitrary write:

    pop rdi ; the_address
    pop rsi ; the_value
    mov [rdi], rsi ; ret

## The use

Plant "/bin/sh" or a GOT overwrite.
