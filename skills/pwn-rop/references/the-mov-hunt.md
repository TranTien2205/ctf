# Hunting mov-store — the write primitive


    /R mov

Then filter for `[rX], rY` patterns — `mov [rdi], rsi; ret` is the
arbitrary write.

## The audit

Read the full tail — a mov-store gadget's extra effects (a second
write, a pop) must be tolerable.
