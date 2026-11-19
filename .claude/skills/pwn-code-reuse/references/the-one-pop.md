# The one-pop call — system alone


system needs only rdi — the minimal chain:

    pop rdi ; "/bin/sh"
    ret           # alignment
    system

Three to four entries — the workhorse ending.
