# Replicating the check — the python model


The solve's proof: a Python re-implementation that produces the
accepted input:

    def check(inp):
        # the transform, byte for byte
        return transformed == STORED

    answer = invert(STORED)     # the accepted input

## The verify

Run the binary with the produced input — the yes-branch executes;
the flag (or the program's success) is observed.
