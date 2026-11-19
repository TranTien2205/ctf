# Verifying against the VM — running it

The produced input verifies by running the actual VM binary:

    ./chal 'produced_flag'    → WIN

or feeding the .pyc / .wasm / bytecode to its interpreter.

## The rule

A decoded program + an inverted transform is a hypothesis — the
accepted input is the solve. Never record the flag until the VM
prints the verdict on YOUR input.

## When the VM won't run

If the binary won't execute (missing dep, arch), replicate the VM
in Python: implement the opcode handlers, run the program bytes —
the inversion stands on the table, not the binary.
