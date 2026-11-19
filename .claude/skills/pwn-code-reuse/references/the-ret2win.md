# ret2win — the simplest chain


If the binary ships a win/flag function: one gadget + the function's
address — the shortest real exploit.

## The recipe

    <padding>
    ret_gadget            # optional, alignment
    win_function_addr

## Falsifier

No win function exists: a real call must be built.
