# rbp and rip — the two saved words


The frame's saved words: saved rbp at ret-8, saved rip at ret — the
overwrite starts at saved rip; rbp's value matters only for leave
pivots.

## The offsets (x64)

    buf_end = saved_rbp
    saved_rbp + 8 = saved_rip

## Falsifier

A different frame layout (frame-pointer-less functions): the save
position differs — disassemble the epilogue.
