# Locating the dispatch loop — deep

Companion to `vm-dispatch-locate.md`.

The loop: read opcode, index handlers, execute — in disasm it's an indexed load in a loop feeding a switch or indirect jump. `r2 -A; pdf @ vm_run`.
