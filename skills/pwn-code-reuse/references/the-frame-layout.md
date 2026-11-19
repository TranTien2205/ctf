# The frame layout — where the chain sits


The overflow buffer's layout past the saved rip:

    [saved rip ← gadget 1]
    [arg for gadget 1]
    [gadget 2]
    [arg for gadget 2]
    [call target]
    [its return slot → next or exit]

## The walk

Each ret consumes the next qword — the stack pointer advances through
the chain as data.
